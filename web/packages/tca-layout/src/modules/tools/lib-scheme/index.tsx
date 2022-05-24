/**
 * 依赖方案配置
 */
import React, { useEffect, useState } from 'react';
import type { MouseEvent } from 'react';
import { Tag, Row, Col, Collapse, Tooltip, message, Modal, Button } from 'coding-oa-uikit';
import TrashIcon from 'coding-oa-uikit/lib/icon/Trash';
import EditIcon from 'coding-oa-uikit/lib/icon/Edit';
import CaretRight from 'coding-oa-uikit/lib/icon/CaretRight';
import CaretDown from 'coding-oa-uikit/lib/icon/CaretDown';

import { getToolSchemes, delToolScheme } from '@src/services/tools';

import UpdateLibSchemeModal from './modal';
import style from '../detail.scss';

const { Panel } = Collapse;

interface LibSchemeProps {
  orgSid: string;
  toolId: number;
  editable: boolean;
}

const LibScheme = (props: LibSchemeProps) => {
  const { orgSid, toolId, editable } = props;
  const [activeKeys, setActiveKeys] = useState<Array<number>>([]);
  const [toolSchemes, setToolSchemes] = useState([]);
  const [modalData, setModalData] = useState({
    visible: false,
    initData: {}
  });

  useEffect(() => getLibSchemes(), [toolId])

  const getLibSchemes = () => {
    getToolSchemes(orgSid, toolId).then((res) => {
      setToolSchemes(res);
      setActiveKeys(res.map((item: any) => item.id))
    })
  }

  const onDelLibScheme = (id: number) => {
    Modal.confirm({
      title: '确定删除该依赖配置?',
      onOk() {
        delToolScheme(orgSid, toolId, id).then(() => {
          message.success('删除成功');
          getLibSchemes();
        })
      }
    });
  }

  return (
    <div className={style.libScheme}>
      <Collapse
        bordered={false}
        activeKey={activeKeys}
        className={style.collapse}
        onChange={(activeKeys: any) => setActiveKeys(activeKeys)}
        expandIcon={({ isActive }) => (isActive ? <CaretDown /> : <CaretRight />)}
      >
        {
          toolSchemes.map((item) => (
            <Panel
              key={item.id}
              className={style.panel}
              header={(
                <>
                  <span>适用于 {item.os?.join('、')} 系统</span>
                  {
                    item.default_flag && (
                      <Tooltip title='所有条件均不满足时使用该方案'>
                        <Tag className={style.defaultTag}>默认方案</Tag>
                      </Tooltip>
                    )
                  }
                </>
              )}
              extra={
                editable && (
                  <>
                    <Tooltip title='编辑'>
                      <EditIcon
                        key='del'
                        onClick={(e: MouseEvent) => {
                          e.stopPropagation();
                          setModalData({
                            visible: true,
                            initData: item
                          })
                        }}
                      />
                    </Tooltip>
                    {
                      // 默认依赖不能删除，当默认依赖为最后一个依赖时可以删除
                      (!item.default_flag || toolSchemes.length === 1) && (
                        <Tooltip title='删除'>
                          <TrashIcon
                            className={style.delIcon}
                            onClick={(e: MouseEvent) => {
                              e.stopPropagation();
                              onDelLibScheme(item.id);
                            }}
                          />
                        </Tooltip>
                      )
                    }
                  </>
                )
              }
            >
              {
                item.condition && (
                  <div className='mb-20'>
                    适用条件：
                    <span className={style.condition}>{item.condition}</span>
                  </div>
                )
              }
              <div className='mb-20'>
                工具依赖：
                {
                  item.toollib_maps?.map((lib: any) => (
                    <Tag key={lib.id}>{lib.toollib.name}</Tag>
                  ))
                }
              </div>
              {
                item.toollib_maps?.some((lib: any) => lib.toollib.envs) && (
                  <div className={style.envsWrapper}>
                    <span>环境变量：</span>
                    <div className={style.envsList}>
                      <Row className={style.row}>
                        <Col span={12} className={style.envKey}>变量名</Col>
                        <Col span={12}>变量值</Col>
                      </Row>
                      {
                        item.toollib_maps?.map((lib: any) => Object.keys(lib.toollib.envs).map((key) => (
                          <Row key={key} className={style.row}>
                            <Col span={12}>{key}</Col>
                            <Col span={12}>{lib.toollib.envs[key]}</Col>
                          </Row>
                        )))
                      }
                      <div className={style.envDesc}>
                        Tips：
                        <p>1. 每个依赖加载后提供的环境变量。</p>
                        <p>2. $ROOT_DIR 表示依赖仓库拉取到本地后的目录路径，会替换成每个依赖目录的实际路径。</p>
                      </div>
                    </div>
                  </div>
                )
              }
            </Panel>
          ))
        }
      </Collapse>
      {
        editable && (
          <Button
            type="primary"
            onClick={() => setModalData({
              visible: true,
              initData: null
            })}
          >
            添加依赖配置
          </Button>
        )
      }
      <UpdateLibSchemeModal
        orgSid={orgSid}
        toolId={toolId}
        visible={modalData.visible}
        initData={modalData.initData}
        toolSchemes={toolSchemes}
        onClose={() => setModalData({
          visible: false,
          initData: null
        })}
        callback={() => {
          getLibSchemes();
        }}
      />
    </div>
  )
}

export default LibScheme;