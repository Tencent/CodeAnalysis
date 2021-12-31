/**
 * description      组合饼图组件
 */

import React from 'react';
import { Chart, Geom, Tooltip, Coord, Label, Legend } from 'bizcharts';
import DataSet from '@antv/data-set';

interface DataCombinatePieProps {
  data: Array<any>,
}

const DataCombinatePie = (props: DataCombinatePieProps) => {
  const dv = new DataSet.DataView();
  dv.source(props.data).transform({
    type: 'percent',
    field: 'value',
    dimension: 'type',
    as: 'percent',
  });
  const cols = {
    percent: {
      formatter: (val) => {
        // eslint-disable-next-line no-param-reassign
        val = `${(val * 100).toFixed(2)}%`;
        return val;
      },
    },
  };
  return (
    <div>
      <Chart height={250} data={dv} scale={cols} padding={[10, 80, 80, 70]} forceFit>
        <Coord type="theta" radius={0.75} innerRadius={0.8} />
        <Legend position="bottom" />
        <Tooltip
          showTitle={false}
          itemTpl='<li><span style="background-color:{color};" class="g2-tooltip-marker"></span>{name}: {value}</li>'
        />
        <Geom
          type="intervalStack"
          position="percent"
          color={['type', ['#ff4c50', '#f5a623', '#ffddd5', '#fff0ed']]}
          tooltip={[
            'item*percent',
            (item, percent) => {
              // eslint-disable-next-line no-param-reassign
              percent = `${(percent * 100).toFixed(2)}%`;
              return {
                name: item,
                value: percent,
              };
            },
          ]}
          style={{
            lineWidth: 1,
            stroke: '#fff',
          }}
        >
          <Label
            content="percent"
            formatter={(val, item) => `${item.point.type}: ${item.point.value}个(${val})`
            }
          />
        </Geom>
      </Chart>
    </div>
  );
};

export default DataCombinatePie;
