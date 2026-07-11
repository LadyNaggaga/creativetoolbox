# Pixel Jam Studio demo — `make demo` runs the whole jam with ZERO Azure and zero key.

PORT ?= 8765
EMU = mock-backends/toolbox_emulator.py

.PHONY: demo play clean help

help:
	@echo "make demo   # run the scripted jam (writes game-output/index.html)"
	@echo "make play   # open the last-built game in your default browser"
	@echo "make clean  # wipe game-output/"

define WITH_EMU
	@TOOLBOX_EMULATOR_PORT=$(PORT) python3 $(EMU) & echo $$! > .emu.pid; \
	sleep 1; \
	( $(1) ); status=$$?; \
	kill `cat .emu.pid` 2>/dev/null; rm -f .emu.pid; \
	exit $$status
endef

demo:
	$(call WITH_EMU, cd python && TOOLBOX_EMULATOR_PORT=$(PORT) python3 main.py)

play:
	@python3 -c "import webbrowser,os; p=os.path.abspath('game-output/index.html'); webbrowser.open('file://'+p); print('opened',p)"

clean:
	@rm -rf game-output .emu.pid
	@find . -name '__pycache__' -type d -prune -exec rm -rf {} + 2>/dev/null || true
