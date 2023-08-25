import React from 'react';
import { t } from '@src/utils/i18n';
import { Button, Space, Tabs, Row, Col } from 'tdesign-react';
import { ChevronRightIcon } from 'tdesign-icons-react';
import Bullhorn from 'coding-oa-uikit/lib/icon/Bullhorn';

import { getMetaContent } from '@tencent/micro-frontend-shared/util';

// 项目内
import SystemModel from '@src/images/system-model.png';
import LangSvg from '@src/images/home/server/lang.svg';
import ArchSvg from '@src/images/home/server/arch.svg';
import CustomSvg from '@src/images/home/server/custom.svg';
import ReportSvg from '@src/images/home/server/report.svg';
import ToolSvg from '@src/images/home/server/tools.svg';
import ScanSvg from '@src/images/home/server/scan.svg';
import scene01 from '@src/images/home/scene/scene01.svg';
import scene02 from '@src/images/home/scene/scene02.svg';
import scene03 from '@src/images/home/scene/scene03.svg';
import customers01 from '@src/images/home/customers/customers01.png';
import customers02 from '@src/images/home/customers/customers02.png';
import customers03 from '@src/images/home/customers/customers03.png';
import customers04 from '@src/images/home/customers/customers04.png';
import customers05 from '@src/images/home/customers/customers05.png';
import customers06 from '@src/images/home/customers/customers06.png';

import s from './style.scss';

// 客户端指引URL地址
const CLIENT_GUIDE_URL = getMetaContent('CLIENT_GUIDE_URL');

const featureItems = [
  {
    title: '稳定可靠的架构',
    desc: '采用分布式云原生架构，支持灵活扩缩容，执行更快更稳定。',
    img: ArchSvg,
    key: 1,
  },
  {
    title: '多工具支持',
    desc: '已集成众多自研、知名开源工具等，采用分层分离架构，满足快速自助管理工具。',
    img: ToolSvg,
    key: 2,
  },
  {
    title: '多语言覆盖',
    desc: '支持29种编程语言，覆盖常见常用编程语言。',
    img: LangSvg,
    key: 3,
  },
  {
    title: '自定义质量指标',
    desc: '自定义代码质量检测标准，逐步优化代码质量。',
    img: CustomSvg,
    key: 4,
  },
  {
    title: '增量全量分析',
    desc: '增量分析快速发现问题，全量分析保证问题全覆盖。',
    img: ScanSvg,
    key: 5,
  },
  {
    title: '全方位质量报告',
    desc: '图形化可视报告，轻松监管代码综合质量趋势。',
    img: ReportSvg,
    key: 6,
  },
];

const customers = [customers01, customers02, customers03, customers04, customers05, customers06];

const Section = () => <>
  {CLIENT_GUIDE_URL && <section className={s.infoSection}>
    {/* <h2 className={s.title}>客户端节点接入</h2> */}
    <div className={s.sectionContainer}>
      <Row>
        <Col span={7}>
          <p className={s.attention}><Bullhorn /> 体验前必读</p>
          <p className={s.title}>客户端节点接入</p>
          <p className={s.pContent}>
            团队专机资源一键接入，自主管控机器资源和编译环境。
            <br />
            分别提供客户端的二进制包和 Docker 镜像，可自由选择安装到专机中，
            <br />
            无需额外部署，方便专机快速接入。
          </p>
          <Button
            className='tca-mt-md'
            href={CLIENT_GUIDE_URL}
            target='_blank'
          >
            <Space size={4} align='center' ><span>{t('节点接入指引')}</span> <ChevronRightIcon /></Space>
          </Button>
        </Col>
        <Col span={5} className='tca-text-right'><img src={SystemModel} width={400} /></Col>
      </Row>
    </div>
  </section>}
  <section className={s.featureSection}>
    <h2>产品特性</h2>
    <div className={s.sectionContent}>
      {/* <h2 className={s.title}>服务优势</h2> */}
      <div className={s.featureContent}>
        {featureItems.map(item => (
          <div className={s.item} key={item.key}>
            <div className={s.img}>
              <img src={item.img} />
            </div>
            <div className={s.tit}>{item.title}</div>
            <div className={s.desc}>{item.desc}</div>
          </div>
        ))}
      </div>
    </div>
  </section>
  <section className={s.scene}>
    <h2>应用场景</h2>
    <Tabs defaultValue="1" size='large'>
      <Tabs.TabPanel label="代码质量分析" value="1">
        <div className={s.tabContent}>
          <p className={s.desc}>腾讯云代码分析支持多语种代码工程质量的监控与分析，可进行增量、全量分析，精确追踪引入问题的责任人，聚合计算代码数据，输出报告。</p>
          <img src={scene01} />
        </div>
      </Tabs.TabPanel>
      <Tabs.TabPanel label="多分支研发流" value="2">
        <div className={s.tabContent}>
          <p className={s.desc}>支持功能分支和主干开发等研发模式，监控代码合流，门禁及时拦截并通知反馈。</p>
          <img src={scene02} />
        </div>
      </Tabs.TabPanel>
      <Tabs.TabPanel label="多平台调用" value="3">
        <div className={s.tabContent}>
          <div className={s.desc}>
            <p>腾讯云代码分析采用分布式客户端，支持云端分析、本地化分析、流水线调度分析等使用场景，满足多样化的研发环境。</p>
            <p className={s.li}>用户可以直接在腾讯云代码分析 SaaS 平台上接入代码库进行云端分析。</p>
            <p className={s.li}>用户可下载客户端，在本地机器上执行代码分析。</p>
            <p className={s.li}>用户可通过 API 开放接口，自行与开源或自研的 DevOps 平台快速集成，满足各类 CI 流水线构建环节的代码分析。</p>
          </div>
          <img src={scene03} />
        </div>
      </Tabs.TabPanel>
    </Tabs>
  </section>
  <section className={s.customers}>
    <h2>客户案例</h2>
    <div className={s.customersContent}>
      {
        customers.map((src: any, index: number) => (
          <div key={index} className={s.customerItem}>
            <span className={s.imgWrapper}>
              <img src={src} />
            </span>
          </div>
        ))
      }
    </div>
  </section>
</>;

export default Section;
