LIBRARY()

LICENSE(
    MIT
)



NO_UTIL()
NO_COMPILER_WARNINGS()

ADDINCL(
    GLOBAL contrib/libs/brotli/include
)

PEERDIR(
    contrib/libs/brotli/common
    contrib/libs/brotli/dec
)

SRCS(
    backward_references.c
    backward_references_hq.c
    bit_cost.c
    block_splitter.c
    brotli_bit_stream.c
    cluster.c
    compress_fragment.c
    compress_fragment_two_pass.c
    dictionary_hash.c
    encode.c
    entropy_encode.c
    histogram.c
    literal_cost.c
    memory.c
    metablock.c
    static_dict.c
    utf8_util.c
)

END()