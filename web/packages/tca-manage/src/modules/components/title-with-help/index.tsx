import React from 'react';

import { Tooltip } from 'tdesign-react';
import { HelpCircleIcon } from 'tdesign-icons-react';
import s from './style.scss';

interface FormLabelWithHelpProps {
  labelString: string;
  helpInfo: string;
}

const FormLabelWithHelp = ({ labelString, helpInfo }: FormLabelWithHelpProps) => (
  <div className={s.formLabel}>
    {labelString}
    <Tooltip
      content={helpInfo}
    >
      <HelpCircleIcon className={s.helpIcon}/>
    </Tooltip>
  </div>
);

export default FormLabelWithHelp;
