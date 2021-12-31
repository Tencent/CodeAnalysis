import React, { useEffect, useState } from 'react';
import ReactDOM from 'react-dom';
import { useHistory } from 'react-router-dom';
import { Layout, Button, Tabs } from 'coding-oa-uikit';

// 项目内
import { t } from '@src/i18n/i18next';
import { enterpriseInfo } from '@src/utils/config';
import { getHomeRouter, getTeamsRouter } from '@src/utils/getRoutePath';

import LangSvg from '@src/images/home/server/lang.svg';
import ArchSvg from '@src/images/home/server/arch.svg';
import CustomSvg from '@src/images/home/server/custom.svg';
import ReportSvg from '@src/images/home/server/report.svg';
import ToolSvg from '@src/images/home/server/tools.svg';
import ScanSvg from '@src/images/home/server/scan.svg';
import CodeBannerPng from '@src/images/code-banner.png';

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

const customers = [customers01, customers02, customers03, customers04, customers05, customers06];

const { Header, Content, Footer } = Layout;

const HeaderRender = () => (
  <Header className={s.header}>
    <a className={s.logo} href={getHomeRouter()}>
      <img src={enterpriseInfo.logo} />
      <div className={s.title}>{enterpriseInfo.name}</div>
    </a>
    <div className={s.right}></div>
  </Header>
);

const BannerRender = () => {
  const history = useHistory();
  const onClick = () => {
    history.push(getTeamsRouter());
  };
  return (
    <div className={s.bannerSection}>
      <div className={s.sectionBg}>
        <div className={s.bgBox}>
          <img
            className={s.pcImg}
            src={CodeBannerPng}
          />
        </div>
      </div>
      <div className={s.sectionContainer}>
        <div className={s.info}>
          <h2 className={s.title}>腾讯云代码分析</h2>
          <p className={s.pContent}>
            用心关注每行代码迭代、助力传承卓越代码文化！
            <br />
            精准跟踪管理代码分析发现的代码质量缺陷、代码规范、代码安全漏洞、无效代码，以及度量代码复杂度、重复代码、代码统计。
          </p>
          <div className={s.btnArea}>
            <Button
              className={s.btn}
              type="link"
              onClick={() => {
                onClick();
              }}
            >
              {t('立即体验')}
            </Button>
          </div>
        </div>
      </div>
    </div>
  );
};

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

const FeatureSectionRender = () => (
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
);

const FooterRender = () => {
  const [year, setYear] = useState<any>();
  useEffect(() => {
    const today = new Date();
    setYear(today.getFullYear());
  }, []);
  return (
    <Footer className={s.footerContainer}>
      <div className={s.footer}>
        <div className="fs18 text-white">
          <p className="mb-xs fs-14">仅限于调试、测试、体验</p>
          <p className="mb-xs">Copyright © 1998 - {year} Tencent. All Rights Reserved.</p>
        </div>
      </div>
    </Footer>
  );
};

const Home = () => {
  const containerNode = document.getElementById('container');
  return (
    <>
      {containerNode
        && ReactDOM.createPortal(
          <div id="home" className={s.home}>
            <HeaderRender />
            <Content className={s.content}>
              <BannerRender />
              <FeatureSectionRender />
              <section className={s.scene}>
                <h2>应用场景</h2>
                <Tabs defaultActiveKey="1" size='large' animated>
                  <Tabs.TabPane tab="代码质量分析" key="1">
                    <div className={s.tabContent}>
                      <p className={s.desc}>腾讯云代码分析支持多语种代码工程质量的监控与分析，可进行增量、全量分析，精确追踪引入问题的责任人，聚合计算代码数据，输出报告。</p>
                      <img src={scene01} />
                    </div>
                  </Tabs.TabPane>
                  <Tabs.TabPane tab="多分支研发流" key="2">
                    <div className={s.tabContent}>
                      <p className={s.desc}>支持功能分支和主干开发等研发模式，监控代码合流，门禁及时拦截并通知反馈。</p>
                      <img src={scene02} />
                    </div>
                  </Tabs.TabPane>
                  <Tabs.TabPane tab="多平台调用" key="3">
                    <div className={s.tabContent}>
                      <div className={s.desc}>
                        <p>腾讯云代码分析采用分布式客户端，支持云端分析、本地化分析、流水线调度分析等使用场景，满足多样化的研发环境。</p>
                        <p className={s.li}>用户可以直接在腾讯云代码分析 SaaS 平台上接入代码库进行云端分析。</p>
                        <p className={s.li}>用户可下载客户端，在本地机器上执行代码分析。</p>
                        <p className={s.li}>用户可通过 API 开放接口，自行与开源或自研的 DevOps 平台快速集成，满足各类 CI 流水线构建环节的代码分析。</p>
                      </div>
                      <img src={scene03} />
                    </div>
                  </Tabs.TabPane>
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

            </Content>
            <FooterRender />
          </div>,
          containerNode,
        )}
    </>
  );
};
export default Home;
