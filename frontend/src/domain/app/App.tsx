import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { QueryClientProvider, QueryClient } from 'react-query';
import { Switch, Route, BrowserRouter } from 'react-router-dom';

import Config from '../config';
import PageLayout from '../../common/layout/PageLayout';
import Stops from '../stops/Stops';
import Routes from '../routes/Routes';

const queryClient = new QueryClient();

function App() {
  const [configReady, setConfigReady] = useState<boolean>(false);

  useEffect(() => {
    // Set global axios settings
    axios.defaults.baseURL = Config.baseUrl;
    axios.defaults.headers.common['authorization'] = `ApiKey ${Config.apiKey}`;
    setConfigReady(true);
  }, []);

  if (!configReady) return null;
  return (
    <QueryClientProvider client={queryClient}>
      <BrowserRouter>
        <PageLayout>
          <Switch>
            <Route exact component={Routes} path={['/', '/routes']} />
            <Route exact component={Stops} path="/stops" />
          </Switch>
        </PageLayout>
      </BrowserRouter>
    </QueryClientProvider>
  );
}

export default App;
