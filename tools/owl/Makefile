.PHONY: build owl tools

BINARY="owl"

darwin:
	CGO_ENABLED=0 GOOS=darwin GOARCH=amd64 go build -o ${BINARY}
	@echo "Compile executable binary for MacOS platform successful."

linux:
	CGO_ENABLED=0 GOOS=linux GOARCH=amd64 go build -o ${BINARY}
	@echo "Compile executable binary for Linux platform successful."

windows:
	CGO_ENABLED=0 GOOS=windows GOARCH=amd64 go build -o ${BINARY}.exe
	@echo "Compile executable binary for Windows platform successful."	

clean:
	@if [ -f ${BINARY} ] ; then rm ${BINARY} ; fi
	@if [ -f ${BINARY}.exe ] ; then rm ${BINARY}.exe ; fi
	@echo "Clean up executable binary successful."

help:
	@echo "make darwin	| Compile executable binary for MacOS platform."
	@echo "make linux	| Compile executable binary for Linux platform."
	@echo "make windows	| Compile executable binary for Windows platform."
	@echo "make clean	| Clean up executable binary."