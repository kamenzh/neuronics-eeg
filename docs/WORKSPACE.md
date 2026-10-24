# Workspace and upstream

Upstream: https://github.com/kamenzh/neuronics-eeg

Base commit: `ae7d76e271737a5eed24690d71cb7defc26290b1`.
Local work branch: `work/neuronic-rev-a`.

This checkpoint is local work based on the public repository, not a claim that
GitHub has been updated. Original non-empty content is preserved in Git history
and `docs/archive/initial-README.md`; only the duplicate starter KiCad placeholders
were removed. The original reference downloads and recovery directory outside
this checkout were left intact.

To use the download, extract its Neuronic folder and open the project directly.
To incorporate it into your own existing clone, first make a Git checkpoint,
then copy the files into your clone, remove the obsolete empty `hardware/pcb_design`
scaffold, and inspect `git diff` before committing. Do not replace the `.git` folder.
