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
	"crypto/md5"
	"encoding/hex"
	"encoding/json"
	"hash"
	"io"
	"io/ioutil"
	"os"
	"path/filepath"
	"time"

	"github.com/auula/owl/log"
)

const (
	// When a single file exceeds this size limit
	// the fragmented md5 algorithm will be used
	fileMaxSize = 10 << 10 << 10 // 10MB

	// Application version information
	Version = "0.1.3"
)

// IsFile check if the path is a file
func IsFile(path string) bool {
	return !IsDir(path)
}

// IsDir check if the path is a directory
func IsDir(path string) bool {
	s, err := os.Stat(path)
	if err != nil {
		return false
	}
	return s.IsDir()
}

// Files returns the collection of all file paths under the specified path
func Files(folder string) ([]string, error) {
	var result []string

	filepath.Walk(folder, func(filePath string, fi os.FileInfo, err error) error {
		if err != nil {
			return err
		}
		if !fi.IsDir() {
			// If you want to ignore this directory, return filepath.SkipDir, ie:
			// return filepath.SkipDir
			result = append(result, filePath)
		}

		return nil
	})

	return result, nil
}

// Md5 get the md5 value of the file based on the path
func Md5(filepath string) (string, error) {
	file, err := os.Open(filepath)
	if err != nil {
		return "", err
	}
	defer file.Close()

	fileInfo, err := os.Stat(filepath)
	if err != nil {
		return "", err
	}

	hashed := md5.New()

	if fileInfo.Size() >= fileMaxSize {
		return BlockMd5(file, fileInfo.Size(), hashed)
	} else {
		io.Copy(hashed, file)
	}

	// io.Copy(hashed, file)

	return hex.EncodeToString(hashed.Sum(nil)), nil
}

// BlockMd5 Built-in sharding md5 algorithm used
func BlockMd5(file *os.File, size int64, hashed hash.Hash) (string, error) {
	// Intercept data segment size window
	var (
		head = make([]byte, 500)
		body = make([]byte, 24)
		tail = make([]byte, 500)
	)

	if _, err := file.ReadAt(head, 0); err != nil {
		return "", err
	}

	if _, err := file.ReadAt(body, size/4); err != nil {
		return "", err
	}

	if _, err := file.ReadAt(tail, size-512); err != nil {
		return "", err
	}
	hashed.Write(head)
	hashed.Write(body)
	hashed.Write(tail)
	return hex.EncodeToString(hashed.Sum(nil)), nil
}

// HexDecode hex decryption
func HexDecode(s string) []byte {
	dst := make([]byte, hex.DecodedLen(len(s)))
	n, err := hex.Decode(dst, []byte(s))
	if err != nil {
		return nil
	}
	return dst[:n]
}

// HexEncode hex encoding
func HexEncode(s string) []byte {
	dst := make([]byte, hex.EncodedLen(len(s)))
	n := hex.Encode(dst, []byte(s))
	return dst[:n]
}

// HexDump convert the specified file to hexadecimal
func HexDump(path string) (string, error) {
	bytes, err := ioutil.ReadFile(path)
	if err != nil {
		return NilString, err
	}
	return hex.Dump(bytes), nil
}

// Scanner universal scanner
type Scanner struct {
	Matcher
	Path string
	Code string
}

// SetMatcher setting matcher scanner
func (s *Scanner) SetMatcher(m Matcher) {
	s.Matcher = m
}

// SetPath setting path scanner
func (s *Scanner) SetPath(path string) {
	s.Path = path
}

// Search search signature
func (s *Scanner) Search(code string) ([]*Result, error) {
	s.Code = code
	if IsDir(s.Path) {
		if files, err := Files(s.Path); err != nil {
			return nil, err
		} else {
			return s.Matcher.Search(files, s.Code)
		}
	}
	return nil, ErrNotIsDir
}

// List returns all files under the specified path to calculate the signature
func (s *Scanner) List() ([]*Result, error) {
	res := make([]*Result, 0)
	if IsFile(s.Path) {
		md5, err := Md5(s.Path)
		if err != nil {
			return nil, err
		}
		res = append(res, &Result{
			Index: 1,
			Path:  s.Path,
			Code:  md5,
		})
		return res, nil
	}

	if files, err := Files(s.Path); err != nil {
		return nil, err
	} else {
		for i, v := range files {
			if md5, err := Md5(v); err != nil {
				return nil, err
			} else {
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

// HexDump convert path content to hexadecimal
func (s *Scanner) HexDump() (string, error) {
	bytes, err := ioutil.ReadFile(s.Path)
	if err != nil {
		return NilString, err
	}
	return hex.Dump(bytes), nil
}

// Exec execution statistics time
func Exec(do func()) {
	defer func() {
		if err := recover(); err != nil {
			log.Warn(err)
			os.Exit(1)
		}
	}()
	log.Info("Loading Files...")
	start := time.Now()
	do()
	elapsed := time.Since(start)
	log.Info("Scanning time to complete: ", elapsed)
	os.Exit(0)
}

// Output output result to writable io device
func (*Scanner) Output(writer io.Writer, res []*Result) error {
	bytes, err := json.Marshal(res)
	if err != nil {
		return err
	}
	if _, err := writer.Write(bytes); err != nil {
		return err
	}
	return nil
}

// Output send the specified content to the console or file
func Output(out string, scanner *Scanner, res []*Result) {
	if out != "" {
		if file, err := os.OpenFile(out, os.O_CREATE|os.O_WRONLY|os.O_TRUNC, 0666); err != nil {
			log.Warn(err)
			file.Close()
			os.Exit(1)
		} else {
			defer file.Close()
			if err := scanner.Output(file, res); err != nil {
				log.Warn(err)
				os.Exit(1)
			}
			log.Info("The result has been redirected to: ", out)
			os.Exit(0)
		}
	}
}

// OutFileString output content to the specified file
func OutFileString(out string, _ *Scanner, hexStr string) {
	if out != "" {
		if file, err := os.OpenFile(out, os.O_CREATE|os.O_WRONLY|os.O_TRUNC, 0666); err != nil {
			log.Warn(err)
			file.Close()
			os.Exit(1)
		} else {
			defer file.Close()
			if _, err := file.WriteString(hexStr); err != nil {
				log.Warn(err)
				os.Exit(1)
			}
			log.Info("The result has been redirected to: ", out)
			os.Exit(0)
		}
	}
}
