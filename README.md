# UAV autonomous control

Install the project with the PyTorch backend appropriate for the machine:

```shell
# macOS or Linux without CUDA
uv sync --extra cpu

# Linux with an NVIDIA driver compatible with CUDA 12.6
uv sync --extra cuda
```

The `dev` group, installed by default by uv, contains visualization tools. Test dependencies remain separate and can be added with `uv sync --extra cpu --group test` or `uv sync --extra cuda --group test`.

See [`docs/PROJECT.md`](docs/PROJECT.md) for the architecture and roadmap.
