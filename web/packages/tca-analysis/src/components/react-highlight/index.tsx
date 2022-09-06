import React, { useRef, useEffect } from 'react';
import hljs from 'highlight.js';


interface HighlightProps {
  children: React.ReactNode | React.ReactNode[];
  element?: React.ReactNode;
  className: any;
}

const Highlight = (props: HighlightProps) => {
  const ele = useRef(null);

  useEffect(() => {
    highlightCode();
  });

  const highlightCode = () => {
    const nodes = ele.current.querySelectorAll('pre code');

    nodes?.forEach((element: any) => {
      hljs.highlightBlock(element);
    });

    // for (let i = 0; i < nodes.length; i++) {
    //   hljs.highlightBlock(nodes[i]);
    // }
  };

  const {
    children,
    className,
    // element: Element = null,
    // innerHTML = false,
  } = props;
  // const eleProps = { ref: ele, className };

  // if (innerHTML) {
  //   eleProps.dangerouslySetInnerHTML = { __html: children };

  //   if (Element) {
  //     return <Element {...eleProps} />;
  //   }
  //   return <div {...eleProps} />;
  // }

  // if (Element) {
  //   return <Element {...eleProps}>{children}</Element>;
  // }
  return <pre ref={ele}><code className={className}>{children}</code></pre>;
};

export default Highlight;
