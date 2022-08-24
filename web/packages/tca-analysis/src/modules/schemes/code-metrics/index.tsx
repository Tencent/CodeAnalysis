// Copyright (c) 2021-2022 THL A29 Limited
//
// This source code file is made available under MIT License
// See LICENSE for details
// ==============================================================================

/**
 * 分析方案 - 代码度量
 */
import React, { useState, useEffect } from 'react';
import cn from 'classnames';
import { pickBy, isNumber } from 'lodash';

import { Form, InputNumber, Tooltip, Switch, Button, message } from 'coding-oa-uikit';
import QuestionCircle from 'coding-oa-uikit/lib/icon/QuestionCircle';

import { getCodeMetrics, updateCodeMetrics } from '@src/services/schemes';


import style from './style.scss';
import formStyle from '../style.scss';

const defaultValues = {
    min_ccn: 20,
    dup_block_length_min: 120,
    dup_min_dup_times: 2,
    dup_issue_limit: 1000,
};

const layout = {
    labelCol: { span: 5 },
    wrapperCol: { span: 19 },
};

interface CodeMetricsProps {
    repoId: number;
    schemeId: number;
    orgSid: string;
    teamName: string;
}

const CodeMetrics = (props: CodeMetricsProps) => {
    const { orgSid, teamName, repoId, schemeId } = props;
    const [form] = Form.useForm();
    const [data, setData] = useState<any>({});

    useEffect(() => {
        getCodeMetrics(orgSid, teamName, repoId, schemeId).then((response: any) => {
            setData(response);
            form.resetFields();
        });
    }, [schemeId]);

    const update = (formData: any, info: string) => {
        updateCodeMetrics(orgSid, teamName, repoId, schemeId, {
            ...data,
            ...formData,
        }).then((response: any) => {
            message.success(`${info}成功`);
            setData(response);
            form.resetFields();
        });
    };

    const onFinish = (formData: any) => {
        update({
            ...formData,
            ...defaultValues,
            ...pickBy(formData, key => isNumber(key)),
        }, '更新');
    };

    return (
        <Form
            labelAlign="left"
            className={cn(style.codeMetrics, formStyle.schemeFormVertical)}
            initialValues={data}
            form={form}
            onFinish={onFinish}
        >
            <h2 className={style.title}>
                圈复杂度
                <Tooltip
                    getPopupContainer={() => document.getElementById('container')}
                    title='可以发现执行路径较多的方法，降低代码的圈复杂度，可测性更高。支持C、C++、Java、C#、JavaScript、Python、Objective-C、Ruby、PHP、Swift、Scala、Go、Lua共13种语言'
                >
                    <QuestionCircle className={formStyle.questionIcon} />
                </Tooltip>
            </h2>
            <Form.Item {...layout} label='是否启用'>
                <Switch
                    size='small'
                    checked={data.cc_scan_enabled}
                    onChange={(checked: boolean) => update({
                        cc_scan_enabled: checked,
                    }, `圈复杂度${checked ? '开启' : '关闭'}`)}
                />
            </Form.Item>
            {
                data.cc_scan_enabled && (
                    <Form.Item
                        {...layout}
                        name='min_ccn'
                        // label='检测阈值'
                        label={
                            <span>
                                检测阈值
                                <Tooltip
                                    getPopupContainer={() => document.getElementById('container')}
                                    title='仅上报圈复杂度超过该阈值的方法，默认20'
                                >
                                    <QuestionCircle className={formStyle.questionIcon} />
                                </Tooltip>
                            </span>
                        }
                    >
                        <InputNumber precision={0} placeholder='默认20' style={{ width: 130 }} />
                    </Form.Item>
                )
            }

            <h2 className={style.title}>
                重复代码
                <Tooltip
                    getPopupContainer={() => document.getElementById('container')}
                    title='可以发现重复的代码，避免重复代码可以让代码更简洁，更易维护。支持C、C++、Java、JavaScript、Objective-C、PHP、Python、C#、Ruby、Kotlin、Go、Lua、Swift、Scala共14种语言'
                >
                    <QuestionCircle className={formStyle.questionIcon} />
                </Tooltip>
            </h2>

            <Form.Item {...layout} label='是否启用'>
                <Switch
                    size='small'
                    checked={data.dup_scan_enabled}
                    onChange={(checked: boolean) => update({
                        dup_scan_enabled: checked,
                    }, `重复代码${checked ? '开启' : '关闭'}`)}
                />
            </Form.Item>
            {
                data.dup_scan_enabled && (
                    <>
                        <Form.Item {...layout}
                            className={style.intervalWrapper}
                            label={
                                <span>
                                    长度区间
                                    <Tooltip
                                        getPopupContainer={() => document.getElementById('container')}
                                        title='一个单词（变量或操作符）记为1'
                                    >
                                        <QuestionCircle className={formStyle.questionIcon} />
                                    </Tooltip>
                                </span>
                            }
                        >
                            <Form.Item name='dup_block_length_min' className={style.interval}>
                                <InputNumber
                                    precision={0}
                                    placeholder='最小默认120'
                                />
                            </Form.Item>
                            <span className={style.splitLine} />
                            <Form.Item name='dup_block_length_max' className={style.interval}>
                                <InputNumber
                                    precision={0}
                                    placeholder='为空默认无限大'
                                />
                            </Form.Item>
                        </Form.Item>
                        <Form.Item {...layout}
                            className={style.intervalWrapper}
                            label={
                                <span>
                                    重复次数
                                    <Tooltip
                                        getPopupContainer={() => document.getElementById('container')}
                                        title='当一段代码重复次数达到指定区间才认为是有风险的'
                                    >
                                        <QuestionCircle className={formStyle.questionIcon} />
                                    </Tooltip>
                                </span>
                            }
                        >
                            <Form.Item name='dup_min_dup_times' className={style.interval}>
                                <InputNumber
                                    precision={0}
                                    placeholder='最小默认2'
                                />
                            </Form.Item>
                            <span className={style.splitLine} />
                            <Form.Item name='dup_max_dup_times' className={style.interval}>
                                <InputNumber
                                    precision={0}
                                    placeholder='为空默认无限大'
                                />
                            </Form.Item>
                        </Form.Item>
                        <Form.Item
                            {...layout}
                            name='dup_issue_limit'
                            label={
                                <span>
                                    上报限制
                                    <Tooltip
                                        getPopupContainer={() => document.getElementById('container')}
                                        title='限制上报的重复代码块数，可以减少开发的压力，提高修复积极性'
                                    >
                                        <QuestionCircle className={formStyle.questionIcon} />
                                    </Tooltip>
                                </span>
                            }
                        >
                            <InputNumber precision={0} placeholder='默认1000' style={{ width: 130 }} />
                        </Form.Item>
                    </>
                )
            }

            <h2 className={style.title}>
                代码统计
                <Tooltip
                    getPopupContainer={() => document.getElementById('container')}
                    title='从目录和业务纬度统计代码行数，也可以获取提交记录便于代码Review。'
                >
                    <QuestionCircle className={formStyle.questionIcon} />
                </Tooltip>
            </h2>
            <Form.Item {...layout} label='是否启用'>
                <Switch
                    size='small'
                    checked={data.cloc_scan_enabled}
                    onChange={(checked: boolean) => update({
                        cloc_scan_enabled: checked,
                    }, `代码统计${checked ? '开启' : '关闭'}`)}
                />
            </Form.Item>

            <Form.Item style={{ marginTop: 30 }}>
                <Button type='primary' htmlType='submit' style={{ marginRight: 10 }}>保存</Button>
                <Button onClick={() => form.resetFields()}>取消</Button>
            </Form.Item>
        </Form>
    );
};

export default CodeMetrics;
