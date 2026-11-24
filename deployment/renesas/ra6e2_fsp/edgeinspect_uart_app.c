/*
 * Minimal RA FSP application example for the EdgeInspect-AI line protocol.
 *
 * This is an integration template, not a ready-to-flash board project. Create
 * an e2 studio project for the exact RA6E2 board, add an SCI UART stack named
 * g_uart0 at 115200 8-N-1 with a callback, and verify the actual UART pins.
 * Generated g_uart0 symbols and board-specific LED functions are required.
 */
#include "hal_data.h"
#include <stdbool.h>
#include <stdint.h>
#include <stdio.h>
#include <string.h>
#include <stdlib.h>

#define EI_LINE_MAX 96U

static volatile char s_rx_line[EI_LINE_MAX];
static volatile uint32_t s_rx_length;
static volatile bool s_line_ready;
static volatile bool s_rx_overflow;
static volatile bool s_discard_until_lf;
static volatile bool s_tx_busy;
static char s_tx_line[EI_LINE_MAX]; /* FSP owns this buffer until TX_COMPLETE. */

typedef struct
{
    int32_t id;
    uint8_t defect_count;
} inspection_message_t;

/* Implement only after matching LED names/polarity to the exact board. */
static void indicate_manual_review(void)
{
    /* TODO: set the board's verified user LED(s) to neutral/manual-review. */
}

static void indicate_decision(const char * decision, const char * severity)
{
    (void) decision;
    (void) severity;
    /* TODO: map to verified onboard LEDs only; keep actuators disconnected. */
}

static bool parse_uint(const char * s, uint32_t min_value, uint32_t max_value, uint32_t * out)
{
    uint32_t value = 0U;
    const char * cursor = s;
    if ((NULL == cursor) || ('\0' == *cursor)) return false;
    while ('\0' != *cursor)
    {
        uint32_t digit;
        if ((*cursor < '0') || (*cursor > '9')) return false;
        digit = (uint32_t) (*cursor - '0');
        if (value > ((max_value - digit) / 10U)) return false;
        value = (value * 10U) + digit;
        ++cursor;
    }
    if (value < min_value) return false;
    *out = value;
    return true;
}

/* Splits exactly seven fields in place; rejects extra or missing separators. */
static bool parse_result(char * line, inspection_message_t * out,
                         char ** mode_out, char ** decision_out, char ** severity_out)
{
    char * fields[7] = {0};
    uint32_t i, id_value, count_value;
    uint32_t field = 0U;

    if ((NULL == line) || (NULL == out)) return false;
    fields[field++] = line;
    for (i = 0U; line[i] != '\0'; ++i)
    {
        if ('|' == line[i])
        {
            if (field >= 7U) return false;
            line[i] = '\0';
            fields[field++] = &line[i + 1U];
        }
    }
    if (field != 7U) return false;
    if ((0 != strcmp(fields[0], "EI1")) || (0 != strcmp(fields[1], "RESULT"))) return false;
    if (!parse_uint(fields[2], 1U, 2147483647U, &id_value)) return false;
    /* Preserve a valid request ID so later field errors can be NACKed to sender. */
    out->id = (int32_t) id_value;
    if ((0 != strcmp(fields[3], "steel")) && (0 != strcmp(fields[3], "pcb"))) return false;
    if ((0 != strcmp(fields[4], "PASS")) && (0 != strcmp(fields[4], "REJECT")) &&
        (0 != strcmp(fields[4], "MANUAL_REVIEW"))) return false;
    if ((0 != strcmp(fields[5], "none")) && (0 != strcmp(fields[5], "minor")) &&
        (0 != strcmp(fields[5], "major")) && (0 != strcmp(fields[5], "critical"))) return false;
    if (!parse_uint(fields[6], 0U, 99U, &count_value)) return false;

    out->defect_count = (uint8_t) count_value;
    *mode_out = fields[3];
    *decision_out = fields[4];
    *severity_out = fields[5];
    return true;
}

static void send_reply(const char * type, int32_t id, const char * code)
{
    int length;
    fsp_err_t err;
    if (s_tx_busy) return;
    length = snprintf(s_tx_line, sizeof(s_tx_line), "EI1|%s|%ld|%s\n",
                          type, (long) id, code);
    if ((length > 0) && ((size_t) length < sizeof(s_tx_line)))
    {
        s_tx_busy = true;
        err = R_SCI_UART_Write(&g_uart0_ctrl, (uint8_t *) s_tx_line, (uint32_t) length);
        if (FSP_SUCCESS != err) s_tx_busy = false;
    }
}

static void handle_line(char * line)
{
    inspection_message_t message = {0};
    char * mode = NULL;
    char * decision = NULL;
    char * severity = NULL;

    if (parse_result(line, &message, &mode, &decision, &severity))
    {
        (void) mode; /* Available for an optional board-side display/log. */
        indicate_decision(decision, severity);
        send_reply("ACK", message.id, "OK");
    }
    else
    {
        indicate_manual_review();
        send_reply("NACK", message.id, "INVALID");
    }
}

void edgeinspect_uart_callback(uart_callback_args_t * p_args)
{
    if (NULL == p_args) return;

    if (UART_EVENT_RX_CHAR == p_args->event)
    {
        char ch = (char) p_args->data;
        if (s_line_ready) return; /* Main loop owns the completed line. */
        if (s_discard_until_lf)
        {
            if ('\n' == ch) s_discard_until_lf = false;
            return;
        }
        if ('\r' == ch) return;
        if ('\n' == ch)
        {
            s_rx_line[s_rx_length] = '\0';
            s_line_ready = true;
        }
        else if (s_rx_length < (EI_LINE_MAX - 1U))
        {
            s_rx_line[s_rx_length++] = ch;
        }
        else
        {
            s_rx_length = 0U;
            s_rx_overflow = true;
            s_discard_until_lf = true;
        }
    }
    else if ((UART_EVENT_ERR_OVERFLOW == p_args->event) ||
             (UART_EVENT_ERR_FRAMING == p_args->event) ||
             (UART_EVENT_ERR_PARITY == p_args->event))
    {
        s_rx_length = 0U;
        s_rx_overflow = true;
        s_discard_until_lf = true;
    }
    else if (UART_EVENT_TX_COMPLETE == p_args->event)
    {
        s_tx_busy = false;
    }
}

void hal_entry(void)
{
    fsp_err_t err = R_SCI_UART_Open(&g_uart0_ctrl, &g_uart0_cfg);
    if (FSP_SUCCESS != err)
    {
        indicate_manual_review();
        while (1) { __NOP(); }
    }

    indicate_manual_review();
    while (1)
    {
        if (s_rx_overflow)
        {
            s_rx_overflow = false;
            s_rx_length = 0U;
            indicate_manual_review();
            send_reply("NACK", 0, "INVALID");
        }
        if (s_line_ready)
        {
            char local_line[EI_LINE_MAX];
            uint32_t i;
            for (i = 0U; i < EI_LINE_MAX; ++i) local_line[i] = s_rx_line[i];
            s_line_ready = false;
            s_rx_length = 0U;
            handle_line(local_line);
        }
        __NOP();
    }
}
