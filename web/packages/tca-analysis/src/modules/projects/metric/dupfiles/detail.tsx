// Copyright (c) 2021-2024 THL A29 Limited
//
// This source code file is made available under MIT License
// See LICENSE for details
// ==============================================================================

// 重复代码详情页
import React, { useEffect, useState } from 'react';
import { useParams } from 'react-router-dom';
import { get, isEmpty, toNumber } from 'lodash';
import {
  Row,
  Col,
  Button,
  Dropdown,
  Menu,
  Select,
  message,
  Input,
  Popover,
} from 'coding-oa-uikit';
import AngleDown from 'coding-oa-uikit/lib/icon/AngleDown';
import AngleUp from 'coding-oa-uikit/lib/icon/AngleUp';
import DotCircle from 'coding-oa-uikit/lib/icon/DotCircle';
import Pencil from 'coding-oa-uikit/lib/icon/Pencil';
// import InfoCircle from 'coding-oa-uikit/lib/icon/InfoCircle';

// 项目内
import { useStateStore } from '@src/context/store';
import CodeHighlight from '@src/components/code-highlight';
import Copy from '@src/components/copy';
import Loading from '@src/components/loading';
import Tips from '@src/components/tips';

import {
  getDupIssuesDetail,
  getDupFileBlocks,
  getDupFileBlockRelatedBlocks,
  getDupCodeFile,
  getDupFileBlockDetail,
  modifyDupFileIssueAuthor,
  modifyDupFileIssueState,
} from '@src/services/projects';
import SelectCodeTipSvg from '@src/images/select-code-tip.svg';

// 模块内
import style from './style.scss';
import { DUP_FILE_STATE_ENUM, DUP_FILE_STATE_OPTIONS } from '../../constants';

const GET_CODE_ENUM = {
  LEFT: 'LEFT',
  RIGHT: 'RIGHT',
};

const DupDetail = () => {
  const [dupFileIssueDetail, setDupFileIssueDetail] = useState<any>(null);

  const [author, setAuthor] = useState('');
  const [authorPopVsb, setAuthorPopVsb] = useState(false);
  const [leftCodeFile, setLeftCodeFile] = useState<any>(null);
  const [leftFileBlocks, setLeftFileBlocks] = useState<Array<any>>([]);
  const [blockDetail, setBlockDetail] = useState<any>(null);
  const [leftResetScrollToLine, setLeftResetScrollToLine] = useState(false);

  const [rightCodeFile, setRightCodeFile] = useState<any>(null);
  const [relatedBlocks, setRelatedBlocks] = useState<Array<any>>([]);
  const [relatedBlock, setRelatedBlock] = useState<any>(null);
  const [rightResetScrollToLine, setRightResetScrollToLine] = useState(false);

  const { curRepo } = useStateStore();
  const params: any = useParams();
  const { orgSid, teamName } = params;
  const repoId = toNumber(params.repoId);
  const projectId = toNumber(params.projectId);
  const issueId = toNumber(params.issueId);

  // 获取重复代码issue信息
  const getIssueDetail = async () => {
    const detail = await getDupIssuesDetail(
      orgSid,
      teamName,
      repoId,
      projectId,
      issueId,
    );
    setDupFileIssueDetail(detail);
    return detail;
  };

  // 获取代码文件内容
  const getCodeFile = async (path: string, revision: string, type: string) => {
    if (type === GET_CODE_ENUM.LEFT) {
      setLeftCodeFile(null);
    } else if (type === GET_CODE_ENUM.RIGHT) {
      setRightCodeFile(null);
    }
    const codefile = await getDupCodeFile(orgSid, teamName, repoId, projectId, {
      path,
      revision,
    });
    if (type === GET_CODE_ENUM.LEFT) {
      setLeftCodeFile(codefile);
    } else if (type === GET_CODE_ENUM.RIGHT) {
      setRightCodeFile(codefile);
    }
    return codefile;
  };

  // 获取当前issue文件的重复块
  const getIssueCodeBlocks = async (blockNum: number) => {
    const res = await getDupFileBlocks(
      orgSid,
      teamName,
      repoId,
      projectId,
      issueId,
      {
        limit: blockNum,
      },
    );
    const blocks = res.results;
    setLeftFileBlocks(blocks);
    return blocks;
  };

  // 获取全部关联的代码块
  const getAllIssueCodeRelateBlocks = async (blockId: number, page = 1) => {
    const offset = (page - 1) * 100;
    const response = await getDupFileBlockRelatedBlocks(
      orgSid,
      teamName,
      repoId,
      projectId,
      issueId,
      blockId,
      { limit: 100, offset },
    );
    let list = get(response, 'results', []);

    if (response.next) {
      list = list.concat(await getAllIssueCodeRelateBlocks(blockId, page + 1));
    }
    return list;
  };

  // 获取当前issue文件选中代码块的全部关联的代码块
  const getIssueCodeRelateBlocks = async (blockId: number) => {
    const blocks = (await getAllIssueCodeRelateBlocks(blockId)) || [];
    setRelatedBlocks(blocks);
  };

  // 选中当前issue文件的某个代码块
  const selectBlockClick = (block: any) => {
    setBlockDetail(block);
    setRelatedBlock(null);
    getIssueCodeRelateBlocks(block.id);
  };

  // 获取代码块详情
  const getIssueCodeBlockDetail = async (blockId: number) => {
    const detail = await getDupFileBlockDetail(
      orgSid,
      teamName,
      repoId,
      projectId,
      issueId,
      blockId,
    );
    selectBlockClick(detail);
    return detail;
  };

  // 初始化
  const init = async () => {
    const detail = await getIssueDetail();
    // 获取代码文件
    getCodeFile(detail.file_path, detail.scm_revision, GET_CODE_ENUM.LEFT);
    const blocks = await getIssueCodeBlocks(detail.block_num);
    // 默认选中第一个
    if (blocks[0]) {
      getIssueCodeBlockDetail(blocks[0].id);
    }
  };

  useEffect(() => {
    init();
  }, []);

  // 修复问题状态
  const modifyIssueState = (id: any, key: string, value: any) => {
    const putData = {
      [key]: value,
    };
    let request;
    switch (key) {
      case 'owner':
        request = modifyDupFileIssueAuthor(
          orgSid,
          teamName,
          repoId,
          projectId,
          id,
          putData,
        );
        break;
      case 'state':
        request = modifyDupFileIssueState(
          orgSid,
          teamName,
          repoId,
          projectId,
          id,
          putData,
        );
        break;
      default:
        break;
    }
    request?.then(() => {
      message.success('修改成功');
      setAuthorPopVsb(false);
      getIssueDetail();
    });
  };

  const handleSelectBlockClick = (e: any) => {
    const block = leftFileBlocks.filter(item => item.id === parseInt(e.key, 10))[0];
    selectBlockClick(block);
  };

  const selectRelateBlockClick = (block: any) => {
    // 如果与现有的代码文件不相同则重新获取
    if (
      !(
        relatedBlock
        && relatedBlock.duplicate_file.file_path
          === block.duplicate_file.file_path
        && relatedBlock.duplicate_file.scm_revision
          === block.duplicate_file.scm_revision
      )
    ) {
      getCodeFile(
        block.duplicate_file.file_path,
        block.duplicate_file.scm_revision,
        GET_CODE_ENUM.RIGHT,
      );
    }
    setRelatedBlock(block);
  };

  const handleSelectRelateBlockClick = (e: any) => {
    const block = relatedBlocks.filter(item => item.id === parseInt(e.key, 10))[0];
    selectRelateBlockClick(block);
  };

  const selectPreOrNextClick = (
    index: number,
    blocks: Array<any>,
    block: any,
    type: string,
  ) => {
    const findex = blocks.findIndex(item => item.id === block.id);
    const newBlock = blocks[findex + index];
    if (newBlock) {
      message.info(`已切换至 ${newBlock.start_line_num} - ${newBlock.end_line_num} 行`);
      if (type === GET_CODE_ENUM.LEFT) {
        selectBlockClick(newBlock);
      } else if (type === GET_CODE_ENUM.RIGHT) {
        selectRelateBlockClick(newBlock);
      }
    } else {
      message.warning('没有更多代码块');
    }
  };

  // 渲染左侧头部信息
  const renderLeftHeader = () => {
    // 前序已校验dupFileIssueDetail存在
    const {
      file_name: fileName,
      dir_path: dirPath,
      block_num: blockNum,
      issue,
      last_modifier: lastModifier,
    } = dupFileIssueDetail;
    return (
      <div className={style.header}>
        <Row gutter={[10, 10]}>
          <Col span={16}>
            <div className="fs-18 text-weight-medium">
              <span className="mr-sm">当前</span>
              {fileName}
            </div>
          </Col>
          <Col span={8} className="text-right">
            {/* TODO：暂时先不实现，后续实现 */}
            {/* <Dropdown
                                overlay={
                                    <Menu>
                                        <Menu.Item key="1">重复率趋势</Menu.Item>
                                        <Menu.Item key="2">操作历史</Menu.Item>
                                    </Menu>
                                }
                            >
                                <Button className="mr-sm" icon={<EllipsisH />} />
                            </Dropdown> */}
            <Dropdown
              overlay={
                <Menu onClick={handleSelectBlockClick}>
                  {leftFileBlocks.map((item: any) => (
                    <Menu.Item key={item.id}>
                      {item.start_line_num} - {item.end_line_num}
                    </Menu.Item>
                  ))}
                </Menu>
              }
            >
              <Button type="primary" style={{ paddingRight: '8px' }}>
                {blockDetail
                  ? `${blockDetail.start_line_num} - ${blockDetail.end_line_num}`
                  : '选择代码块'}
                <span style={{ marginLeft: '16px', opacity: '0.6' }}>|</span>
                <AngleDown />
              </Button>
            </Dropdown>
          </Col>
          <Col className="fs-12 text-grey-6 ellipsis" span={12}>
            路径：{dirPath}
          </Col>
          <Col className="fs-12 text-grey-6 ellipsis" span={12}>
            仓库地址：{curRepo.scm_url}{' '}
            <Copy text={curRepo.scm_url} copyText={curRepo.scm_url} />
          </Col>
          <Col span={24}>
            <div className={style.headerDetailOp}>{blockNum} 块重复</div>{' '}
            <div className={style.headerDetailOp}>
              <span className="mr-sm">责任人</span>
              {issue.owner}
              {issue.state === DUP_FILE_STATE_ENUM.ACTIVE && (
                <Popover
                  title="修改责任人"
                  placement="bottom"
                  visible={authorPopVsb}
                  overlayClassName={style.statusPopover}
                  content={
                    <div>
                      <Input
                        placeholder="请输入责任人"
                        size="middle"
                        value={author}
                        onChange={e => setAuthor(e.target.value)}
                      />
                      <div className={style.footer}>
                        <Button
                          size="small"
                          type="primary"
                          onClick={() => {
                            modifyIssueState(issue.id, 'owner', author);
                          }}
                        >
                          确认
                        </Button>
                        <Button
                          size="small"
                          onClick={() => {
                            setAuthorPopVsb(false);
                            setAuthor('');
                          }}
                        >
                          取消
                        </Button>
                      </div>
                    </div>
                  }
                >
                  <Tips
                    icon={
                      <Pencil
                        className={style.editIcon}
                        onClick={() => {
                          setAuthorPopVsb(!authorPopVsb);
                        }}
                      />
                    }
                    title="修改责任人"
                  />
                </Popover>
              )}
            </div>
            <div className={style.headerDetailOp}>
              <span className="mr-sm">状态</span>
              <Select
                value={issue.state}
                onChange={(value: any) => modifyIssueState(issue.id, 'state', value)
                }
                options={DUP_FILE_STATE_OPTIONS.map(item => ({
                  label: item.text,
                  value: item.value,
                }))}
                dropdownMatchSelectWidth={false}
                bordered={false}
              />
            </div>
          </Col>
          {blockDetail && (
            <Col className="fs-12 text-grey-6 ellipsis">
              当前查看的{blockDetail.start_line_num} -{' '}
              {blockDetail.end_line_num} 行代码被 {lastModifier}最近修改过
            </Col>
          )}
        </Row>
      </div>
    );
  };

  // 渲染右侧头部
  const renderRightHeader = () => (
    <div className={style.header}>
      {relatedBlock && (
        <Row gutter={[10, 10]}>
          <Col flex="auto">
            <div className="fs-18 text-weight-medium">
              <span className="mr-sm">对比</span>
              <Select
                style={{ fontSize: '18px' }}
                optionLabelProp="label"
                dropdownMatchSelectWidth={false}
                bordered={false}
                value={relatedBlock ? relatedBlock.id : undefined}
                onChange={(value: number) => handleSelectRelateBlockClick({ key: value })
                }
              >
                {relatedBlocks.map((item: any) => (
                  <Select.Option
                    key={item.id}
                    value={item.id}
                    label={item.duplicate_file.file_name}
                  >
                    <h4>{item.duplicate_file.file_name}</h4>
                    <div className="fs-12 text-grey-6">
                      <div>
                        对比行：{item.start_line_num} - {item.end_line_num}
                      </div>
                      <div>文件路径：{item.duplicate_file.dir_path}</div>
                    </div>
                  </Select.Option>
                ))}
              </Select>
            </div>
          </Col>
          <Col flex="none"></Col>
          <Col className="fs-12 text-grey-6 ellipsis" span={24}>
            路径：{relatedBlock.duplicate_file.dir_path}
          </Col>
          <Col span={24}>
            <div className={style.headerDetailOp}>
              代码块：{relatedBlock.start_line_num} -{' '}
              {relatedBlock.end_line_num} 行
            </div>{' '}
            <div className={style.headerDetailOp}>
              {relatedBlock.last_modifier} 最近修改过
            </div>{' '}
          </Col>
          <Col className="fs-12 text-grey-6 ellipsis">
            共有 {relatedBlocks.length} 个代码文件块与当前代码块重复
          </Col>
        </Row>
      )}
    </div>
  );

  // 渲染代码块
  const renderCodeContainer = (
    codefile: any,
    block: any,
    resetScrollToLine = false,
  ) => (
    <div className={style.container}>
      {codefile ? (
        <CodeHighlight
          resetScrollToLine={resetScrollToLine}
          scrollToLine={block ? block.start_line_num : 1}
          codefile={codefile}
          rowStyle={(lineNum: number) => {
            if (
              block
              && block.start_line_num <= lineNum
              && lineNum <= block.end_line_num
            ) {
              return {
                borderLeftColor: '#fbd341',
              };
            }
            return {};
          }}
        />
      ) : (
        <Loading />
      )}
    </div>
  );

  // 渲染右侧内容
  const renderRightContainer = () => {
    if (relatedBlock) {
      return (
        <>
          {renderRightHeader()}
          <Row className="my-sm">
            <Col flex="auto">
              <Button
                className="mr-sm"
                icon={<AngleUp />}
                onClick={() => selectPreOrNextClick(
                  -1,
                  relatedBlocks,
                  relatedBlock,
                  GET_CODE_ENUM.RIGHT,
                )
                }
              >
                上一处
              </Button>
              <Button
                className="mr-sm"
                icon={<AngleDown />}
                onClick={() => selectPreOrNextClick(
                  1,
                  relatedBlocks,
                  relatedBlock,
                  GET_CODE_ENUM.RIGHT,
                )
                }
              >
                下一处
              </Button>
              <Button
                icon={<DotCircle />}
                onClick={() => setRightResetScrollToLine(!rightResetScrollToLine)
                }
              />
            </Col>
            <Col flex="none">
              {/* <Select
                value={theme}
                onChange={(value: any) => setTheme(value)}
                options={CODE_THEME_OPTIONS}
                dropdownMatchSelectWidth={false}
                bordered={false}
              ></Select> */}
            </Col>
          </Row>
          {renderCodeContainer(
            rightCodeFile,
            relatedBlock,
            rightResetScrollToLine,
          )}
        </>
      );
    }
    return (
      <div className={style.middleBlock}>
        <img src={SelectCodeTipSvg} alt="select-code-tip" />
        {isEmpty(blockDetail) ? (
          <>
            <p>请先在左侧选择一个代码块进行查看</p>
          </>
        ) : (
          <>
            <h4>请选择一个对比文件查看</h4>
            <p className="mb-md">
              共有 {relatedBlocks.length} 个代码文件块与当前代码块重复
            </p>
            <Select
              style={{ width: '270px', textAlign: 'left' }}
              placeholder="请选择对比文件块"
              value={relatedBlock ? relatedBlock.id : undefined}
              onChange={(value: number) => handleSelectRelateBlockClick({ key: value })
              }
            >
              {relatedBlocks.map((item: any) => (
                <Select.Option key={item.id} value={item.id}>
                  <h4>{item.duplicate_file.file_name}</h4>
                  <div className="fs-12 text-grey-6">
                    <div>
                      对比行：{item.start_line_num} - {item.end_line_num}
                    </div>
                    <div>文件路径：{item.duplicate_file.dir_path}</div>
                  </div>
                </Select.Option>
              ))}
            </Select>
          </>
        )}
      </div>
    );
  };

  if (!dupFileIssueDetail) {
    return <></>;
  }

  return (
    <Row className={style.dupFileContainer}>
      <Col span={12}>
        <div className={style.leftContainer}>
          {renderLeftHeader()}
          <Row className="my-sm">
            <Col flex="auto">
              <Button
                className="mr-sm"
                icon={<AngleUp />}
                onClick={() => selectPreOrNextClick(
                  -1,
                  leftFileBlocks,
                  blockDetail,
                  GET_CODE_ENUM.LEFT,
                )
                }
              >
                上一处
              </Button>
              <Button
                className="mr-sm"
                icon={<AngleDown />}
                onClick={() => selectPreOrNextClick(
                  1,
                  leftFileBlocks,
                  blockDetail,
                  GET_CODE_ENUM.LEFT,
                )
                }
              >
                下一处
              </Button>
              <Button
                icon={<DotCircle />}
                onClick={() => setLeftResetScrollToLine(!leftResetScrollToLine)}
              />
            </Col>
            <Col flex="none">
              {/* <Select
                value={theme}
                onChange={(value: any) => setTheme(value)}
                options={CODE_THEME_OPTIONS}
                dropdownMatchSelectWidth={false}
                bordered={false}
              ></Select> */}
            </Col>
          </Row>
          {renderCodeContainer(
            leftCodeFile,
            blockDetail,
            leftResetScrollToLine,
          )}
        </div>
      </Col>
      <Col span={12}>
        <div className={style.rightContainer}>{renderRightContainer()}</div>
      </Col>
    </Row>
  );
};

export default DupDetail;
