import React from 'react';
import ReactDOM from 'react-dom';

interface ContainerProps {
  children: any;
}

const Container = (props: ContainerProps) => {
  const containerNode = document.getElementById('container');
  const { children } = props;

  return <>{containerNode && ReactDOM.createPortal(children, containerNode)}</>;
};

export default Container;
