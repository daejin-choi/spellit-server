#!/usr/bin/env bash
mkdir -p packages/
pushd packages/
BASE_URL="http://pypi.python.org/packages/source"
if [[ ! -d feedparser-5.0.1 ]]; then
  curl $BASE_URL/f/feedparser/feedparser-5.0.1.tar.gz | tar xvfz -
fi
cp feedparser-5.0.1/feedparser/{feedparser,sgmllib3}.py ./
if [[ ! -d Flask-0.8 ]]; then
  curl $BASE_URL/F/Flask/Flask-0.8.tar.gz | tar xvfz -
fi
cp -r Flask-0.8/flask ./
if [[ ! -d Werkzeug-0.8.1 ]]; then
  curl $BASE_URL/W/Werkzeug/Werkzeug-0.8.1.tar.gz | tar xvfz -
fi
cp -r Werkzeug-0.8.1/werkzeug ./
if [[ ! -d pyasn1-0.1.1 ]]; then
  curl $BASE_URL/p/pyasn1/pyasn1-0.1.1.tar.gz | tar xvfz -
fi
cp -r pyasn1-0.1.1/pyasn1 ./
if [[ ! -d rsa-3.0.1 ]]; then
  curl -O $BASE_URL/r/rsa/rsa-3.0.1.zip
  unzip rsa-3.0.1.zip
  rm rsa-3.0.1.zip
fi
cp -r rsa-3.0.1/rsa ./
zip -r site-packages.zip feedparser.py sgmllib3.py flask werkzeug pyasn1 rsa
mv site-packages.zip ../spellit/
popd
