// MIT License

// Copyright (c) 2022 Leon Ding <ding@ibyte.me>

// Permission is hereby granted, free of charge, to any person obtaining a copy
// of this software and associated documentation files (the "Software"), to deal
// in the Software without restriction, including without limitation the rights
// to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
// copies of the Software, and to permit persons to whom the Software is
// furnished to do so, subject to the following conditions:

// The above copyright notice and this permission notice shall be included in all
// copies or substantial portions of the Software.

// THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
// IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
// FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
// AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
// LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
// OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
// SOFTWARE.

package scan_test

import (
	"crypto/md5"
	"os"
	"testing"

	"github.com/auula/owl/scan"
	"github.com/stretchr/testify/assert"
)

func TestAllFunction(t *testing.T) {
	assert.Equal(t, true, scan.IsDir("/"))
	assert.Equal(t, true, scan.IsFile("scanner_test.go"))

	files, err := scan.Files("./")
	if err != nil {
		t.Fatal(err)
	}
	assert.Equal(t, []string{"matcher.go", "scanner.go", "scanner_test.go"}, files)

	assert.Equal(t, func() string {
		md5, _ := scan.Md5("scanner_test.go")
		return md5
	}(), func() string {
		md5, _ := scan.Md5("scanner_test.go")
		return md5
	}())

	assert.Equal(t, scan.HexDecode("scanner_test.go"), scan.HexDecode("scanner_test.go"))
	assert.Equal(t, scan.HexEncode("scanner_test.go"), scan.HexEncode("scanner_test.go"))

	assert.Equal(t, func() string {
		strHex, _ := scan.HexDump("scanner_test.go")
		return strHex
	}(), func() string {
		strHex, _ := scan.HexDump("scanner_test.go")
		return strHex
	}())
}

func TestBlackMd5(t *testing.T) {
	file, err := os.Open("scanner_test.go")
	if err != nil {
		t.Fatal(err)
	}
	fi, err := os.Stat("scanner_test.go")
	if err != nil {
		t.Fatal(err)
	}
	assert.Equal(t, func() string {
		md5, _ := scan.BlockMd5(file, fi.Size(), md5.New())
		return md5
	}(), func() string {
		md5, _ := scan.BlockMd5(file, fi.Size(), md5.New())
		return md5
	}())
}

func TestScanner(t *testing.T) {
	scanner := new(scan.Scanner)
	scanner.SetPath("./")
	res, err := scanner.List()
	if err != nil {
		t.Fatal(err)
	}
	t.Log(res)

	scanner.SetMatcher(new(scan.Md5Matcher))
	res, err = scanner.Search("xxxx")
	if err != nil {
		t.Fatal(err)
	}
	if len(res) != 0 {
		t.Fatal(res)
	}

	scanner.SetPath("scanner_test.go")
	assert.Equal(t, func() string {
		str, _ := scanner.HexDump()
		return str
	}(), func() string {
		str, _ := scanner.HexDump()
		return str
	}())

	file, err := os.OpenFile("res.json", os.O_CREATE|os.O_RDWR|os.O_TRUNC, 0666)
	if err != nil {
		t.Fatal(err)
	}
	if err := scanner.Output(file, res); err != nil {
		t.Fatal(err)
	}
	os.Remove("res.json")
}
