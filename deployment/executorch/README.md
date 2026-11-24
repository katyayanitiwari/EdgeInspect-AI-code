# Optional local Llama + ExecuTorch advisor

## What is implemented in the app

`inference/advisor.py` has an opt-in adapter for ExecuTorch's Python `NativeLlamaRunner`. The deterministic rule-based advisor remains the default. If the private Python environment, `.pte`, params, or tokenizer is absent—or the generated explanation does not mention a reported defect class—the app uses rule-based guidance. The fixed rule decision is always authoritative. The Llama text is a separate, optional explanation.

The private laptop copy now contains authorized model files and an exported `.pte`; both are excluded from uploads under `LOCAL_ONLY_DO_NOT_UPLOAD/`. Laptop software inference has been smoke-run with ExecuTorch's Python `NativeLlamaRunner`. **No C++ runner or board/FPGA inference result is claimed.** Model files must remain under their license terms.

## Recommended first experiment

Use Llama 3.2 1B with ExecuTorch's documented XNNPACK CPU path as a starting point. The official ExecuTorch guide lists Llama 3.2 as supported and describes exporting to `.pte`, then running it with the C++ runner. This recommendation is a starting experiment only; memory, speed, output quality, and compatibility on KV260 or Pi 5 have not been measured.

Official references:

- [ExecuTorch LLM export guide](https://github.com/pytorch/executorch/blob/main/docs/source/llm/export-llm.md)
- [ExecuTorch Llama example and runner](https://github.com/pytorch/executorch/blob/main/examples/models/llama/README.md)
- [ExecuTorch LLM getting started](https://github.com/pytorch/executorch/blob/main/docs/source/llm/getting-started.md)

## Authorized model download (Windows)

After the model owner has approved access and the Hugging Face CLI is installed and logged in, run this from the project root:

```powershell
powershell.exe -NoProfile -ExecutionPolicy Bypass -File .\deployment\executorch\download_llama.ps1
```

The script downloads only the three required files to `LOCAL_ONLY_DO_NOT_UPLOAD/Llama_3_2_1B/`. It does not put weights or tokens in the source package. Keep this folder private and excluded from Git/ZIP uploads. If approval is unavailable, skip this step; do not use an unauthorized mirror.
## Export recipe (Linux build environment)

1. Install a mutually compatible ExecuTorch/PyTorch toolchain following the official setup guide. The current Windows laptop environment is not the target Linux runtime.
2. Obtain the Llama 3.2 1B checkpoint, `params.json`, and tokenizer through an authorized source. The model files are intentionally not committed here.
3. Edit `llama3_2_1b_xnnpack.yaml`: replace the two absolute checkpoint/parameter paths and use the exact metadata values supplied for the chosen model artifact.
4. From the ExecuTorch checkout/environment, run:

   ```bash
   python -m executorch.extension.llm.export.export_llm \
     --config /path/to/EdgeInspect-AI/deployment/executorch/llama3_2_1b_xnnpack.yaml
   ```

5. Save the exporter log and its delegated/non-delegated operator report. Find the generated `.pte` from the exporter output; do not assume the default artifact path.
6. Build the Llama runner using the official example instructions for the **same target architecture and runtime**. Confirm its CLI by running `llama_main --help` on that build.
7. First run a neutral prompt on the target. Then configure the dashboard environment below and inspect whether the runner's stdout contains only usable generated text. No application integration is complete until this output path is validated on the target.

The quantization/backend recipe follows ExecuTorch's published XNNPACK LLM example. Hardware compatibility and performance still require a real target run.

## Current laptop preparation

The BHARAT EDGE copy has an isolated Windows CPU environment under `LOCAL_ONLY_DO_NOT_UPLOAD/executorch-system-env`. The approved model was exported to a private 802 MB XNNPACK `.pte`. To start the optional laptop dashboard with Llama explanations, use:

```powershell
.\run_dashboard_with_llama_windows.bat
```

This uses the private ExecuTorch Python runner and starts a new process per inspection, so model load time can be noticeable. Keep all source model files, tokenizer, `.pte`, environment, and logs under `LOCAL_ONLY_DO_NOT_UPLOAD/` out of source uploads.

## Enable the adapter

Set these variables in the same shell that starts the dashboard:

```bash
export EDGEINSPECT_ADVISOR=executorch
set EDGEINSPECT_EXECUTORCH_PYTHON=/absolute/path/to/executorch-python.exe
export EDGEINSPECT_LLM_MODEL=/absolute/path/to/model.pte
export EDGEINSPECT_LLM_PARAMS=/absolute/path/to/params.json
export EDGEINSPECT_LLM_TOKENIZER=/absolute/path/to/tokenizer.model
export EDGEINSPECT_LLM_TIMEOUT=180
```

Unset `EDGEINSPECT_ADVISOR` or set it to `rules` to use the deterministic advisor. If ExecuTorch is selected but files are missing, the application safely falls back to rules. The adapter currently starts the configured native runner as a new process for each inspection; that may reload the model each time and cause long delays. The default timeout is 60 seconds. A persistent runner service would be needed for a responsive repeated-inspection workflow, and its performance must be measured on the target.

## Validation still required

- Review the generated explanation with varied genuine inspection reports; reject generic or irrelevant text.
- Build/run a compatible ExecuTorch runtime for the intended Arm/Linux target and verify `.pte` plus tokenizer load.
- Measure cold load time, generation latency, peak RAM, artifact size, and offline behavior on each target.
- Record cold load time, generation latency, peak RAM, model/artifact size, and offline operation.
- Compare outputs against the rule-based reference on saved examples; reject any LLM response that invents a defect or changes the decision.
