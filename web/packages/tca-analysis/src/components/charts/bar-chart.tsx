/**
 * description    柱状图封装
 */

import React from 'react';
import { Chart, Geom, Axis, Tooltip, Legend } from 'bizcharts';

interface BarChartProps {
  data: any,
  xAxisKey: string,
  yAxisKey: string,
  cols: any,
}

const BarChart = (props: BarChartProps) => {
  const { data, xAxisKey, yAxisKey, cols } = props;
  return (
      <div>
        <Chart height={250} data={data} scale={cols} forceFit>
          <Axis
            name={xAxisKey}
            label={{
              formatter(text) {
                return text.split('(')[0];
              },
            }}
          />
          <Axis name={yAxisKey} />
          <Legend position="bottom" />
          <Tooltip
            crosshairs={{
              type: 'y',
            }}
          />
          <Geom
            type="interval"
            size="25"
            position={`${xAxisKey}*${yAxisKey}`}
            color={[xAxisKey, ['#3655b3', '#5870fe', '#9ab3ff', '#c0d1ff']]}
            tooltip={[
              `${xAxisKey}*${yAxisKey}`,
              (x, y) => ({
                name: x.split('(')[0],
                title: x.split('(')[0],
                value: y,
              }),
            ]}
          />
        </Chart>
      </div>
  );
};

export default BarChart;
