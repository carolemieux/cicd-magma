FROM ubuntu:22.04
# This is the Dockerfile for getting coverage values

# TODO remove sudo for user "magma" to avoid unwanted priv escalation from
# other attack vectors.

RUN apt-get update && apt-get install -y sudo vim

## Magma directory hierarchy
# magma_root is relative to the docker-build's working directory
# The Docker image must be built in the root of the magma directory
ARG magma_root=./

# avoid interactive installation
ENV DEBIAN_FRONTEND=noninteractive 

## Path variables inside the container
ENV MAGMA_R /magma
ENV OUT		/magma_out
ENV SHARED 	/magma_shared

ENV CC  /usr/bin/gcc
ENV CXX /usr/bin/g++
ENV LD /usr/bin/ld
ENV AR /usr/bin/ar
ENV AS /usr/bin/as
ENV NM /usr/bin/nm
ENV RANLIB /usr/bin/ranlib

ARG USER_ID=1000
ARG GROUP_ID=1000
RUN mkdir -p /home && \
	groupadd -g ${GROUP_ID} magma && \
	useradd -l -u ${USER_ID} -K UMASK=0000 -d /home -g magma magma && \
	chown magma:magma /home
RUN	echo "magma:amgam" | chpasswd && usermod -a -G sudo magma

RUN mkdir -p ${SHARED} ${OUT} && \
	chown magma:magma ${SHARED} ${OUT} && \
	chmod 744 ${SHARED} ${OUT}

RUN chown magma:magma /usr/include/
RUN chown magma:magma /usr/local/
RUN mkdir -p /usr/lib/bfd-plugins/ && \
	chown magma:magma /usr/lib/bfd-plugins/

ARG magma_path=magma
ENV MAGMA 	${MAGMA_R}/${magma_path}
USER root:root
RUN mkdir -p ${MAGMA} && chown magma:magma ${MAGMA}
COPY --chown=magma:magma ${magma_root}/${magma_path} ${MAGMA}/
RUN ${MAGMA}/preinstall.sh
USER magma:magma
RUN ${MAGMA}/prebuild.sh

ARG fuzzer_name
ARG fuzzer_path=fuzzers/${fuzzer_name}
ENV FUZZER 	${MAGMA_R}/${fuzzer_path}
USER root:root
RUN mkdir -p ${FUZZER} && chown magma:magma ${FUZZER}
COPY --chown=magma:magma ${magma_root}/${fuzzer_path} ${FUZZER}/

RUN ${FUZZER}/preinstall.sh
RUN ${FUZZER}/fetch.sh
RUN ${FUZZER}/build.sh
# changed the user 
USER magma:magma

ARG target_name
ARG target_path=targets/${target_name}
ENV TARGET 	${MAGMA_R}/${target_path}
USER root:root
RUN mkdir -p ${TARGET} && chown magma:magma ${TARGET}
COPY --chown=magma:magma ${magma_root}/${target_path} ${TARGET}/
RUN ${TARGET}/preinstall.sh
USER magma:magma
RUN ${TARGET}/fetch.sh
RUN ${MAGMA}/apply_patches.sh

ARG corpus_name
ARG seed_path=seed/${corpus_name}
ENV SEED	${TARGET}/corpus/seed
USER root:root
RUN mkdir -p ${SEED} && chown magma:magma ${SEED}
COPY --chown=magma:magma ${magma_root}/${seed_path} ${SEED}/
USER magma:magma

# ARG corpus_name
# ARG seed_path1=seed/afl/${target_name}
# ARG seed_path2=seed/aflpp/${target_name}
# ARG seed_path3=seed/aflgo/${target_name}
# ARG seed_path4=seed/ffd/${target_name}
# ARG seed_path5=seed/libfuzzer/${target_name}
# ARG seed_path6=seed/aflgoexp/${target_name}

# ENV SEED 	${TARGET}/corpus/seed
# USER root:root
# RUN mkdir -p ${SEED}/afl && chown magma:magma ${SEED}/afl && chown magma:magma ${SEED}
# RUN mkdir -p ${SEED}/aflpp && chown magma:magma ${SEED}/aflpp
# RUN mkdir -p ${SEED}/aflgo && chown magma:magma ${SEED}/aflgo 
# RUN mkdir -p ${SEED}/ffd && chown magma:magma ${SEED}/ffd
# RUN mkdir -p ${SEED}/libfuzzer && chown magma:magma ${SEED}/libfuzzer
# RUN mkdir -p ${SEED}/aflgoexp && chown magma:magma ${SEED}/aflgoexp && chown magma:magma ${SEED}

# COPY --chown=magma:magma ${magma_root}/${seed_path1} ${SEED}/afl
# COPY --chown=magma:magma ${magma_root}/${seed_path2} ${SEED}/aflpp
# COPY --chown=magma:magma ${magma_root}/${seed_path3} ${SEED}/aflgo
# COPY --chown=magma:magma ${magma_root}/${seed_path4} ${SEED}/ffd
# COPY --chown=magma:magma ${magma_root}/${seed_path5} ${SEED}/libfuzzer
# COPY --chown=magma:magma ${magma_root}/${seed_path6} ${SEED}/aflgoexp
# USER magma:magma

## Configuration parameters
ARG isan
ARG harden
ARG canaries
ARG fixes

ARG ISAN_FLAG=${isan:+-DMAGMA_FATAL_CANARIES}
ARG HARDEN_FLAG=${harden:+-DMAGMA_HARDEN_CANARIES}
ARG CANARIES_FLAG=${canaries:+-DMAGMA_ENABLE_CANARIES}
ARG FIXES_FLAG=${fixes:+-DMAGMA_ENABLE_FIXES}
ARG BUILD_FLAGS="-include ${MAGMA}/src/canary.h ${CANARIES_FLAG} ${FIXES_FLAG} ${ISAN_FLAG} ${HARDEN_FLAG} -g -O0"

ENV CFLAGS ${BUILD_FLAGS}
ENV CXXFLAGS ${BUILD_FLAGS}
ENV LIBS -l:magma.o -lrt
ENV LDFLAGS -L"${OUT}" -g

RUN ${FUZZER}/instrument.sh

ENTRYPOINT "${MAGMA}/run.sh"
