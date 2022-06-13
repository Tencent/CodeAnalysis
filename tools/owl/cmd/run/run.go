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

package run

import (
	"os"

	"github.com/auula/owl/log"
	"github.com/auula/owl/scan"
	"github.com/auula/owl/table"
	"github.com/fatih/color"
	"github.com/spf13/cobra"
)

const (
	helpLong = `
 
	Example:

	Scan the target data file or directory according to different feature codes 👇
	$ ./owl run --dir=/user/desktop/directory --mode=md5 --code=81129dsxxxxx2d8123

	Search according to different patterns 👇
	$ ./owl run --dir=/user/desktop/directory --mode=hex --code=74 63 61 73 63 61 6e 2f --out=result.json
	`
)

var mode, code, dir, out string

var Cmd = cobra.Command{
	Use:   "run",
	Short: "Execute the scanner",
	Long:  color.GreenString(helpLong),
	Run: func(cmd *cobra.Command, args []string) {
		scan.Exec(func() {
			scanner := new(scan.Scanner)
			scanner.SetPath(dir)
			switch mode {
			case "md5":
				scanner.SetMatcher(new(scan.Md5Matcher))
			case "hex":
				scanner.SetMatcher(new(scan.HexMatcher))
			default:
				log.Warn("Match search pattern is not sure")
				os.Exit(1)
			}
			if code == "" {
				log.Warn("Match value can not be empty can be md5 or hexadecimal string")
				os.Exit(1)
			}
			if res, err := scanner.Search(code); err != nil {
				log.Warn(err)
				os.Exit(1)
			} else {
				scan.Output(out, scanner, res)
				table.WriteTables(table.CommonTemplate, res)
			}
		})
	},
}

func init() {
	Cmd.Flags().StringVar(&code, "code", "", "Requires search signature")
	Cmd.Flags().StringVar(&mode, "mode", "", "Matcher search mode")
	Cmd.Flags().StringVar(&dir, "dir", "", "Directory path to scan")
	Cmd.Flags().StringVar(&out, "out", "", "Data result output is saved to the specified file")
}
