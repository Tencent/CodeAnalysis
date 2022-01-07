// Copyright (c) 2021-2022 THL A29 Limited
//
// This source code file is made available under MIT License
// See LICENSE for details
// ==============================================================================

/**
 * description      折线图组件
 */
// @ts-nocheck
import React from 'react';
import { Chart, Geom, Axis, Tooltip } from 'bizcharts';
import s from './style.scss';

interface LineProps {
  title: string,
  data: Array<any>,
  xAxisKey: string,
  yAxisKey: string,
  cols: any,
  height: string,
  padding: string | number
  | { top: number; right: number; bottom: number; left: number; }
  | [number, number, number, number] | [string, string],
}

const Line = (props: LineProps) => {
  const { height, data, cols, xAxisKey, yAxisKey, title, padding } = props;
  return (
    <>
      <Chart
        height={height || 250}
        data={data}
        scale={cols}
        forceFit
        padding={padding || [10, 'auto', 80, 'auto']}
      >
        <p className={`${s.title} ${s.title_with_border}`}>{title}</p>
        <Axis name={xAxisKey} />
        <Tooltip
          crosshairs={{
            type: 'y',
          }}
        />
        <Geom
          type="line"
          position={`${xAxisKey}*${yAxisKey}`}
          size={2}
          color={['type', ['#0066ff']]}
        />
        <Geom
          type="area"
          position={`${xAxisKey}*${yAxisKey}`}
          color={[
            'type',
            ['l (90) 0:rgba(0, 102, 255, 0.3) 1:rgba(0, 102, 255, 0.1)'],
          ]}
          tooltip={false}
        />
      </Chart>
    </>
  );
};

export default Line;
