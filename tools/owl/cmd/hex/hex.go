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

package hex

import (
	"fmt"
	"os"

	"github.com/auula/owl/log"
	"github.com/auula/owl/scan"
	"github.com/fatih/color"
	"github.com/spf13/cobra"
)

const (
	helpLong = `
 
	Example:
	
	File that needs to be converted to hex 👇
	$ ./owl hex --path=/user/desktop/test.txt

	A file that needs to be converted to hex and redirected output 👇
	$ ./owl hex --path=/user/desktop/test.txt --out=result.json
	`
)

var path, out string

var Cmd = cobra.Command{
	Use:   "hex",
	Short: "File hex encoding",
	Long:  color.GreenString(helpLong),
	Run: func(cmd *cobra.Command, args []string) {
		scanner := new(scan.Scanner)
		scanner.SetPath(path)
		if hexStr, err := scanner.HexDump(); err != nil {
			log.Warn(err)
			os.Exit(1)
		} else {
			scan.OutFileString(out, scanner, hexStr)
			fmt.Println(color.GreenString(hexStr))
		}
	},
}

func init() {
	Cmd.Flags().StringVar(&out, "out", "", "Data result output is saved to the specified file")
	Cmd.Flags().StringVar(&path, "path", "", "The path to the file that needs to be converted to a hexadecimal string")
}
