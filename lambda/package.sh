 GOARCH="amd64" GOOS="linux" go build . ; go build main.go  ; chmod 755 main ; zip function.zip main restore-from-snapshot
