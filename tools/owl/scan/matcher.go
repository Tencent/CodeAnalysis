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

package scan

import (
	"errors"
	"strings"
)

var (
	ErrNotIsDir = errors.New("the current file is not a directory")
	NilString   = ""
)

// Result content scan results
type Result struct {
	Index int    `json:"index,omitempty"`
	Path  string `json:"path,omitempty"`
	Code  string `json:"code,omitempty"`
}

// Matcher scanner matcher
type Matcher interface {
	Search(files []string, searchTerm string) ([]*Result, error)
}

type (
	// Matcher md5 and  hex implement
	Md5Matcher struct{}
	HexMatcher struct{}
)

// Search match search signatures by md5 in file collections
func (*Md5Matcher) Search(files []string, searchTerm string) ([]*Result, error) {
	res := make([]*Result, 0)
	for i, v := range files {
		if md5, err := Md5(v); err != nil {
			return nil, err
		} else {
			if md5 == searchTerm {
				res = append(res, &Result{
					Index: i + 1,
					Path:  v,
					Code:  md5,
				})
			}
		}
	}
	return res, nil
}

// Search match search signatures by hex in file collections
func (*HexMatcher) Search(files []string, searchTerm string) ([]*Result, error) {
	res := make([]*Result, 0)
	for i, v := range files {
		strHex, err := HexDump(v)
		if err != nil {
			return nil, err
		}
		if strings.Contains(strHex, searchTerm) {
			md5, err := Md5(v)
			if err != nil {
				return nil, err
			}
			res = append(res, &Result{
				Index: i + 1,
				Path:  v,
				Code:  md5,
			})
		}
	}
	return res, nil
}
