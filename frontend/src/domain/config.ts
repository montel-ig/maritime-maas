class Config {
  static get apiKey() {
    return process.env.REACT_APP_MAAS_API_KEY;
  }

  static get baseUrl() {
    return process.env.REACT_APP_MAAS_BASE_URL;
  }
}

export default Config;
