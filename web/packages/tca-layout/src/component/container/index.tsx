import React from 'react';
import ReactDOM from 'react-dom';

interface ContainerProps {
  children: any;
}

const containerNode = document.getElementById('container');

/** 用于将内容放入container div内 */
const Container = ({ children }: ContainerProps) => <>
  {containerNode && ReactDOM.createPortal(children, containerNode)}
</>;

export default Container;
