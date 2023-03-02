// Copyright (c) 2021-2022 THL A29 Limited
//
// This source code file is made available under MIT License
// See LICENSE for details
// ==============================================================================

/* eslint-disable */
import React, { Component } from 'react';
import * as d3 from 'd3';
import { isString, get } from 'lodash';

import { Upload, message } from 'coding-oa-uikit';

import style from './style.scss';

const { Dragger } = Upload;
const width = 700;
const height = 700;

interface IProps {
  params?: any;
}

interface IState {
  files: any;
}

class CirclePacking extends Component<IProps, IState> {
  constructor(props: any) {
    super(props);
    this.state = {
      files: [],
    };
  }

  pack = (data: any) => d3.pack()
    .size([width, height])
    .padding(3)
    (d3.hierarchy(data)
      .sum((d: any) => Number(d.size))
      .sort((a: any, b: any) => Number(b.size) - Number(a.size)));


  getCircle = (data: any) => {
    const root = this.pack(data);
    let focus = root;
    let view: any;

    const color = d3.scaleLinear()
      .domain([-1, 5])
      .range(['hsl(185, 60%, 99%)', 'hsl(187, 40%, 70%)'])
      .interpolate(d3.interpolateHcl);

    const svg = d3.select('#dropBox').append('svg')
      .attr('viewBox', `-${width / 2} -${height / 2} ${width} ${height}`)
      .style('display', 'block')
      .style('margin', '-14px')
      // .style("background", color(0))
      .style('cursor', 'pointer')
      // .attr("transform", "translate(" + 10 + "," + 10 + ")")
      .on('click', () => zoom(root));

    const node = svg.append('g')
      .selectAll('circle')
      .data(root.descendants().slice(1))
      .join('circle')
      .attr('fill', (d: any) => (d.children ? color(d.depth) : '#3D98FF'))
      .style('fill-opacity', (d: any) => get(d, 'data.weight', 1))
      .attr('pointer-events', (d: any) => (!d.children ? 'none' : null))
      .on('mouseover', function () {
        d3.select(this).attr('stroke', '#6FA2A9');
      })
      .on('mouseout', function () {
        d3.select(this).attr('stroke', null);
      })
      .on('click', (d: any) => focus !== d && (zoom(d), d3.event.stopPropagation()));

    const label = svg.append('g')
      .style('font', '14px sans-serif')
      .attr('pointer-events', 'none')
      .attr('text-anchor', 'middle')
      .selectAll('text')
      .data(root.descendants())
      .join('text')
      .style('fill-opacity', (d: any) => (d.parent === root ? 1 : 0))
      .style('display', (d: any) => (d.parent === root ? 'inline' : 'none'))
      .text((d: any) => d.data.name);

    zoomTo([root.x, root.y, root.r * 2]);

    function zoomTo(v: any) {
      const k = width / v[2];

      view = v;

      label.attr('transform', (d: any) => `translate(${(d.x - v[0]) * k},${(d.y - v[1]) * k})`);
      node.attr('transform', (d: any) => `translate(${(d.x - v[0]) * k},${(d.y - v[1]) * k})`);
      node.attr('r', (d: any) => d.r * k);
    }

    const zoom = (d: any) => {
      const focus0 = focus;

      focus = d;

      const transition = svg.transition()
        .duration(d3.event.altKey ? 7500 : 750)
        .tween('zoom', () => {
          const i = d3.interpolateZoom(view, [focus.x, focus.y, focus.r * 2]);
          return (t: any) => zoomTo(i(t));
        });

      label
        .filter(function (d: any) {
          return d.parent === focus || this.style.display === 'inline';
        })
        .transition(transition)
        .style('fill-opacity', (d: any) => (d.parent === focus ? 1 : 0))
        .on('start', function (d: any) {
          if (d.parent === focus) this.style.display = 'inline';
        })
        .on('end', function (d: any) {
          if (d.parent !== focus) this.style.display = 'none';
        });
    };
  };

  beforeUpload = (file: any) => {
    const reader = new FileReader();
    const _this = this;

    this.setState({ files: [...this.state.files, file] });
    reader.readAsText(file, 'UTF-8');
    reader.onload = function (e) {
      if (this.result) {
        let data = {};
        if (isString(this.result)) {
          try {
            data = JSON.parse(this.result as string);
          } catch (e) {
            message.error('json文件格式不准确');
          }
        } else {
          data = this.result;
        }
        _this.getCircle(data);
      }
    };

    return false;
  };

  onRemoveFile = (file: any) => {
    const { files } = this.state;
    d3.selectAll('#dropBox svg').remove();

    const curFiles = files.filter((item: any) => item.uid !== file.uid);
    curFiles.map((item: any) => {
      const reader = new FileReader();
      const _this = this;

      reader.readAsText(item, 'UTF-8');
      reader.onload = function (e) {
        if (this.result) {
          let data = {};
          if (isString(this.result)) {
            try {
              data = JSON.parse(this.result as string);
            } catch (e) {
              message.error('json文件格式不准确');
            }
          } else {
            data = this.result;
          }
          _this.getCircle(data);
        }
      };
    });
    this.setState({ files: curFiles });
  };

  render() {
    return (
      <div>
        <Dragger className={style.dragger} beforeUpload={this.beforeUpload} onRemove={this.onRemoveFile}>
          请点击上传或者拖拽原始数据文件到这里
        </Dragger>
        <div className={style.dropBox} id='dropBox'></div>
      </div>
    );
  }
}

export default CirclePacking;
