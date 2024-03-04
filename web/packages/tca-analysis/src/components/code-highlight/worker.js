// Copyright (c) 2021-2024 THL A29 Limited
//
// This source code file is made available under MIT License
// See LICENSE for details
// ==============================================================================

const workercode = () => {
  onmessage = (event) => {
    // eslint-disable-next-line no-undef
    importScripts('https://cdnjs.cloudflare.com/ajax/libs/highlight.js/10.7.1/highlight.min.js');
    const codedfile = event.data;
    const suffixSpt = codedfile.suffix ? codedfile.suffix.split('.') : null;
    const suffix = suffixSpt && suffixSpt.length > 1 ? suffixSpt[1] : null;
    const language = codedfile.language ? codedfile.language : suffix || 'plaintext';
    const codeContents = codedfile.codeContents.map((v) => {
      const content = self.hljs.highlightAuto(`${v.content} `, [language]).value;
      return {
        content,
        lineNum: v.lineNum,
      };
    });
    codedfile.codeContents = codeContents;
    postMessage(codedfile);
  };
};

// 把脚本代码转为string
let code = workercode.toString();
code = code.substring(code.indexOf('{') + 1, code.lastIndexOf('}'));

const blob = new Blob([code], { type: 'application/javascript' });
const workerScript = URL.createObjectURL(blob);

module.exports = workerScript;
