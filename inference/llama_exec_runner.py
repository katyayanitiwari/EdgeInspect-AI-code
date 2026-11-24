"""Run a local ExecuTorch Llama export and return only its generated explanation."""
from __future__ import annotations

import argparse
import json
from types import SimpleNamespace


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--model", required=True)
    parser.add_argument("--params", required=True)
    parser.add_argument("--tokenizer", required=True)
    parser.add_argument("--prompt", required=True)
    args = parser.parse_args()

    # Import inside main so help and argument errors remain quick and clear.
    from executorch.examples.models.llama.runner.native import NativeLlamaRunner

    runner = NativeLlamaRunner(
        SimpleNamespace(
            params=args.params,
            tokenizer=args.tokenizer,
            tokenizer_config=None,
            max_len=128,
            kv_cache=True,
            pte=args.model,
        )
    )
    # Llama 3.2 Instruct expects the model's chat boundary tokens. Encode those
    # as special tokens instead of ordinary printable text.
    tokens = runner.tokenizer.encode(
        args.prompt, bos=False, eos=False, allowed_special="all"
    )
    if len(tokens) >= 127:
        raise ValueError(
            f"Prompt is too long for this exported model: {len(tokens)} tokens; max is 126."
        )
    generated = runner.generate(
        prompt_tokens=tokens,
        max_seq_len=128,
        temperature=0.1,
        top_p=0.9,
    )
    text = runner.tokenizer.decode(generated).strip()
    print("EDGEINSPECT_RESULT:" + text, flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
