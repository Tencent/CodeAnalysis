// Copyright (c) 2021-2024 THL A29 Limited
//
// This source code file is made available under MIT License
// See LICENSE for details
// ==============================================================================

// 代码高亮自定义组件
import React, { useRef, useEffect, CSSProperties } from 'react';
import { VariableSizeList as List } from 'react-window';
import AutoSizer from 'react-virtualized-auto-sizer';
import Highlight from 'react-highlight';
import s from './style.scss';

interface IFileProps {
  suffix: string;
  codeContents: Array<any>;
  language: string;
  file_path: string;
  scm_revision: string;
}

interface IProps {
  theme?: string;
  codefile: IFileProps;
  defaultRowHeight?: number;
  rowStyle?: (lineNum: number) => CSSProperties;
  rowLineStyle?: (lineNum: number) => CSSProperties;
  rowStartRender?: (lineNum: number, content: string) => React.ReactNode;
  rowEndRender?: (lineNum: number, content: string) => React.ReactNode;
  scrollToLine?: number;
  resetScrollToLine?: boolean;
}

interface ICodeListProps extends IProps {
  width: number;
  height: number;
}

/**
 * 计算文本内容宽度大小
 * @param text 文本内容
 * @returns width 宽度
 */
const computedMaxLineWidth = (text: any) => {
  const span = document.createElement('span');
  let width = span.offsetWidth;
  span.style.visibility = 'hidden';
  span.style.display = 'inline-block';
  document.body.appendChild(span);
  if (typeof span.textContent !== 'undefined') {
    span.textContent = text;
  } else {
    span.innerText = text;
  }
  width = parseFloat(window.getComputedStyle(span).width) - width;
  document.body.removeChild(span);
  return width;
};

/**
 * 格式化代码文件
 * @param codefile 代码文件
 * @returns { contents, language, maxLineWidth }
 */
const formatCodeFile = (codefile: IFileProps) => {
  const suffixSpt = codefile.suffix ? codefile.suffix.split('.') : null;
  const suffix = suffixSpt && suffixSpt.length > 1 ? suffixSpt[1] : null;
  const language = codefile.language ? codefile.language : suffix || 'plaintext';
  const contents = codefile.codeContents;
  const last = contents[contents.length - 1];
  const maxLineWidth = computedMaxLineWidth(last ? last.lineNum : 100);
  return { contents, language, maxLineWidth };
};

const CodeList = ({
  width,
  height,
  codefile,
  defaultRowHeight = 30,
  rowStyle = () => ({}),
  rowLineStyle = () => ({}),
  rowStartRender = () => <></>,
  rowEndRender = () => <></>,
  scrollToLine = 1,
  resetScrollToLine = false,
}: ICodeListProps) => {
  const listRef: any = useRef(null);
  const rowHeights: any = useRef({});
  const { contents, language, maxLineWidth } = formatCodeFile(codefile);

  // 高度计算，最小defaultRowHeight
  const getRowHeight = (index: number) => (rowHeights.current[index]
    > defaultRowHeight ? rowHeights.current[index] : defaultRowHeight);

  const setRowHeight = (index: number, size: number) => {
    listRef.current.resetAfterIndex(0);
    rowHeights.current = { ...rowHeights.current, [index]: size };
  };

  // 渲染每行
  const RowRender = ({ index, style }: any) => {
    const rowRef = useRef<HTMLDivElement>(null);

    useEffect(() => {
      if (rowRef.current) {
        setRowHeight(index, rowRef.current.clientHeight);
      }
    }, [rowRef]);

    const { content, lineNum } = contents[index];
    return (
      <div className={s.codeHighLightRow} style={style}>
        <span className={s.codeLine} style={{ flex: `0 0 ${maxLineWidth + 20}px`, ...rowLineStyle(lineNum) }}>{lineNum}</span>
        <div
          ref={rowRef}
          className={s.codeContent}
          style={{ ...rowStyle(lineNum) }}
        >
          {rowStartRender(lineNum, content)}
          <Highlight className={language}>{`${content} `}</Highlight>
          {rowEndRender(lineNum, content)}
        </div>
      </div>
    );
  };

  // 因为AutoSizer它需要一些时间才能呈现其子级，因此将其放入子级内触发
  useEffect(() => {
    if (scrollToLine) {
      listRef.current.scrollToItem(scrollToLine - 1, 'start');
    }
  }, [scrollToLine, resetScrollToLine]);
  return (
    <List
      height={height}
      itemCount={contents.length}
      itemSize={getRowHeight}
      width={width}
      ref={listRef}
    >
      {RowRender}
    </List>
  );
};

const CodeHighlight = (props: IProps) => (
  <>
    <link
      rel="stylesheet"
      href="https://highlightjs.org/static/demo/styles/default.css"
    />
    <AutoSizer>
      {({ height, width }) => <CodeList width={width} height={height} {...props} />}
    </AutoSizer>
  </>
);

export default CodeHighlight;
