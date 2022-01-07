// Copyright (c) 2021-2022 THL A29 Limited
//
// This source code file is made available under MIT License
// See LICENSE for details
// ==============================================================================

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
