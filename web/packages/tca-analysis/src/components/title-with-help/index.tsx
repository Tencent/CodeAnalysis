import React from 'react';
import cn from 'classnames';
import { Tooltip } from 'tdesign-react';
import { HelpCircleIcon } from 'tdesign-icons-react';
import s from './style.scss';

interface FormLabelWithHelpProps {
  labelString: string;
  helpInfo: string;
  size?: 'small' | 'large';
}

const FormLabelWithHelp = ({ labelString, helpInfo, size = 'small' }: FormLabelWithHelpProps) => (
  <div className={cn(s.formLabel, s[`${size}-label`])}>
    {labelString}
    <Tooltip
      content={helpInfo}
    >
      <HelpCircleIcon className={s.helpIcon}/>
    </Tooltip>
  </div>
);

export default FormLabelWithHelp;
