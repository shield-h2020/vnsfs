FROM centos:7

ENV GOLANG_URL https://storage.googleapis.com/golang/go1.7.linux-amd64.tar.gz
ENV GOLANG_TAR go1.7.linux-amd64.tar.gz
ENV SHA256SUM 702ad90f705365227e902b42d91dd1a40e48ca7f67a2f4b2fd052aaa4295cd95
ENV GOBIN="$HOME/go/bin"
ENV GOPATH="$HOME/go/src"
ENV PATH=$PATH:/usr/local/go/bin
ENV GOROOT=/usr/local/go


RUN yum -y --setopt=tsflags=nodocs update && \
    yum -y --setopt=tsflags=nodocs install curl 

RUN echo "$SHA256SUM  $GOLANG_TAR" > sha256 && \ 
    curl -l0 https://storage.googleapis.com/golang/go1.7.linux-amd64.tar.gz -o $GOLANG_TAR

RUN sha256sum -c sha256 && \
    tar -C /usr/local -zxvf go1.7.linux-amd64.tar.gz

RUN mkdir -p ~/go/{bin,pkg,src}
COPY ./* ./
CMD ["./mspltranslator","-input","*.mspl"]
