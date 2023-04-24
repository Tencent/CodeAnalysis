/**
 * 用户引导
 */
import React, { useState, useEffect, useRef } from 'react';
import { Guide } from 'tdesign-react';

import s from './style.scss';

export const renderGuideDialog = (descriptions: string[], img?: string) => (
  <div className={s.guideDialog}>
    {descriptions.map((des: string, idx: number) => <p key={`guide_${idx}`}>{des}</p>)}
    {img && <div><img className="img" src={img} /></div>}
  </div>
);

interface UserGuideProps {
  keyword: string,
  steps: any[],
  mode?: 'popup' | 'dialog',
  showGuide?: boolean,
}

const UserGuide = ({ keyword, steps, showGuide, mode = 'popup' }: UserGuideProps) => {
  const [current, setCurrent] = useState(-1);
  const timer = useRef<any>(null);

  useEffect(() => {
    setCurrent(-1);
    const skip = (localStorage.getItem(`tca_guide_${keyword}`) === 'skip');
    if (!skip && showGuide) {
      timer.current = setTimeout(() => {
        clearTimer();
        const validSteps = steps?.every(s => !!document.querySelector(s?.element));
        validSteps && setCurrent(0);
      }, 500);
    }
    return clearTimer;
  }, [showGuide, keyword, steps]);

  /** 清除定时器 */
  const clearTimer = () => {
    if (timer.current) {
      clearTimeout(timer.current);
      timer.current = null;
    }
  };

  const setSkip = () => {
    localStorage.setItem(`tca_guide_${keyword}`, 'skip');
  };

  const handleChange = (current: number) => {
    setCurrent(current);
  };

  return (
    <Guide
      current={current}
      steps={steps}
      onChange={handleChange}
      onFinish={setSkip}
      onSkip={setSkip}
      mode={mode}
    />
  );
};

export default UserGuide;
