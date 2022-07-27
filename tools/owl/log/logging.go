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

package log

import (
	"log"
	"os"

	"github.com/fatih/color"
)

var (
	info *log.Logger
	warn *log.Logger
)

var (
	// Logger colors and log message prefixes
	warnOut   = color.New(color.FgWhite, color.Bold, color.BgRed).Sprintf("WARN:")
	infoOut   = color.New(color.FgWhite, color.Bold, color.BgGreen).Sprintf("INFO:")
	redFont   = color.New(color.FgRed)
	greenFont = color.New(color.FgGreen)
)

const (
	// Logger message format
	format = log.Ldate | log.Ltime
)

func init() {
	info = log.New(os.Stdout, infoOut, format)
	warn = log.New(os.Stdout, warnOut, format)
}

func Info(v ...any) {
	info.Output(2, greenFont.Sprint(v...))
}

func Warn(v ...any) {
	warn.Output(2, redFont.Sprint(v...))
}
