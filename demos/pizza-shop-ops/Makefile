# Pizza Shop Ops — toolbox-demo-builder demo
# `make demo` runs the magic moment with ZERO Azure and zero model key.

PORT ?= 8765
EMU = mock-backends/toolbox_emulator.py

.PHONY: demo demo-dotnet demo-all gif clean help

help:
	@echo "make demo         # python scripted demo (no Azure, no key)"
	@echo "make demo-dotnet  # C# scripted demo (parity)"
	@echo "make demo-all     # both"
	@echo "make gif          # record assets/demo.gif (needs vhs)"

# start emulator, run a command against it, always stop the emulator
define WITH_EMU
	@TOOLBOX_EMULATOR_PORT=$(PORT) python3 $(EMU) & echo $$! > .emu.pid; \
	sleep 1; \
	( $(1) ); status=$$?; \
	kill `cat .emu.pid` 2>/dev/null; rm -f .emu.pid; \
	exit $$status
endef

demo:
	$(call WITH_EMU, cd python && TOOLBOX_EMULATOR_PORT=$(PORT) python3 main.py)

demo-dotnet:
	$(call WITH_EMU, cd dotnet && TOOLBOX_EMULATOR_PORT=$(PORT) dotnet run)

demo-all: demo demo-dotnet

gif:
	@command -v vhs >/dev/null 2>&1 || { echo "install vhs: https://github.com/charmbracelet/vhs"; exit 1; }
	vhs demo.tape

clean:
	@rm -f .emu.pid assets/demo.gif
	@find . -name '__pycache__' -type d -prune -exec rm -rf {} + 2>/dev/null || true
