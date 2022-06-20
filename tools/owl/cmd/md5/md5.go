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

package md5

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
	
	Get the md5 value of the specified file 👇
	$ ./owl md5 --path=/user/desktop/test.txt

	Get the md5 value of all files in the specified directory 👇
	$ ./owl md5 --path=/user/desktop/directory --out=result.json
	`
)

var path, out string

var Cmd = cobra.Command{
	Use:   "md5",
	Short: "Collection file md5",
	Long:  color.GreenString(helpLong),
	Run: func(cmd *cobra.Command, args []string) {
		scan.Exec(func() {
			scanner := new(scan.Scanner)
			scanner.SetPath(path)
			if res, err := scanner.List(); err != nil {
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
	Cmd.Flags().StringVar(&out, "out", "", "Data result output is saved to the specified file")
	Cmd.Flags().StringVar(&path, "path", "", "The file path where the md5 value needs to be obtained")
}
