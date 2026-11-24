param(
    [Parameter()]
    [string]$Port = 'COM13',
    [Parameter()]
    [int]$Baud = 115200
)

# Minimal interactive serial console. Keys go directly to the connected board;
# received text is shown here. It does not save or log typed input.
$serial = [System.IO.Ports.SerialPort]::new(
    $Port, $Baud, [System.IO.Ports.Parity]::None, 8, [System.IO.Ports.StopBits]::One
)
$serial.Handshake = [System.IO.Ports.Handshake]::None
$serial.ReadTimeout = 100
$serial.WriteTimeout = 1000

try {
    $serial.Open()
    [Console]::WriteLine("Connected to $Port at $Baud baud. Ctrl+C exits this console.")
    [Console]::WriteLine('Board keystrokes are not saved by this script. Password input should remain hidden by Linux.')
    # Nudge the login service to redraw its prompt if boot completed before this console attached.
    $serial.Write("`r")
    Start-Sleep -Milliseconds 250

    while ($true) {
        if ($serial.BytesToRead -gt 0) {
            [Console]::Write($serial.ReadExisting())
        }

        if ([Console]::KeyAvailable) {
            $key = [Console]::ReadKey($true)
            if ($key.Key -eq [ConsoleKey]::C -and
                ($key.Modifiers -band [ConsoleModifiers]::Control)) {
                break
            }
            elseif ($key.Key -eq [ConsoleKey]::Enter) {
                $serial.Write("`r")
            }
            elseif ($key.Key -eq [ConsoleKey]::Backspace) {
                $serial.Write([string][char]8)
            }
            elseif (-not [char]::IsControl($key.KeyChar)) {
                $serial.Write([string]$key.KeyChar)
            }
        }
        Start-Sleep -Milliseconds 10
    }
}
finally {
    if ($serial.IsOpen) { $serial.Close() }
    $serial.Dispose()
    [Console]::WriteLine("`nDisconnected from $Port.")
}
