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

package cmd

import (
	"fmt"
	"os"

	"github.com/auula/owl/cmd/hex"
	"github.com/auula/owl/cmd/md5"
	"github.com/auula/owl/cmd/run"
	"github.com/auula/owl/cmd/version"
	"github.com/auula/owl/log"
	"github.com/auula/owl/scan"
	"github.com/fatih/color"
	"github.com/spf13/cobra"
)

const (
	bannerStr = `
			 _____  _    _  __   
			(  _  )( \/\/ )(  )  
			 )(_)(  )    (  )(__ 
			(_____)(__/\__)(____) 🦉 %s 
   
 A dependency module feature scanning detection tool for static analysis.
`
)

var banner string = color.CyanString(fmt.Sprintf(bannerStr, scan.Version))

var rootCmd = &cobra.Command{
	Use:   "owl",
	Short: "Owl is a dependency module feature scanning detection tool for static analysis.",
	Long:  banner,
}

func Execute() {
	if err := rootCmd.Execute(); err != nil {
		log.Warn(err)
		os.Exit(1)
	}
}

func init() {
	rootCmd.AddCommand(&version.Cmd)
	rootCmd.AddCommand(&run.Cmd)
	rootCmd.AddCommand(&md5.Cmd)
	rootCmd.AddCommand(&hex.Cmd)
}
