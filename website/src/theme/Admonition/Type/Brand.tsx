import React, { type ReactNode } from 'react';
import clsx from 'clsx';
import type { Props } from '@theme/Admonition';
import AdmonitionLayout from '@theme/Admonition/Layout';

const infimaClassName = 'alert alert--brand';

const defaultProps = {
  icon: '',
  title: '',
};

export default function AdmonitionTypeBrand(props: Props): ReactNode {
  return (
    <AdmonitionLayout
      {...defaultProps}
      {...props}
      type="brand"
      className={clsx(infimaClassName, props.className)}
    >
      {props.children}
    </AdmonitionLayout>
  );
}
