import React, { ReactElement } from 'react';
import { Link } from 'react-router-dom';

import styles from './pageLayout.module.css';

type Props = {
  children: ReactElement;
};

const PageLayout = ({ children }: Props) => {
  return (
    <>
      <header className={styles.header}>
        <Link to="/routes" className={styles.link}>
          Routes
        </Link>
        <Link to="/stops" className={styles.link}>
          Stops
        </Link>
      </header>
      <main className={styles.main}>{children}</main>
    </>
  );
};

export default PageLayout;
