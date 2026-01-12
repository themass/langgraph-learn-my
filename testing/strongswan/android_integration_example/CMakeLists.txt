# CMakeLists.txt for strongSwan Android Integration Example
cmake_minimum_required(VERSION 3.18.1)

project("strongswan_integration")

# 设置 C++ 标准
set(CMAKE_CXX_STANDARD 17)

# 添加头文件目录
include_directories(
    ${CMAKE_CURRENT_SOURCE_DIR}/include
    ${CMAKE_CURRENT_SOURCE_DIR}/include/strongswan
    ${CMAKE_CURRENT_SOURCE_DIR}/include/charon
    ${CMAKE_CURRENT_SOURCE_DIR}/include/ipsec
)

# 添加源文件
set(SOURCES
    src/main.cpp
    src/strongswan_manager.cpp
    src/vpn_connection.cpp
)

# 创建共享库
add_library(strongswan_integration SHARED ${SOURCES})

# 添加 strongSwan 库 (从 jniLibs 目录)
add_library(strongswan SHARED IMPORTED)
set_target_properties(strongswan PROPERTIES
    IMPORTED_LOCATION ${CMAKE_CURRENT_SOURCE_DIR}/../jniLibs/${ANDROID_ABI}/libstrongswan.so)

add_library(charon SHARED IMPORTED)
set_target_properties(charon PROPERTIES
    IMPORTED_LOCATION ${CMAKE_CURRENT_SOURCE_DIR}/../jniLibs/${ANDROID_ABI}/libcharon.so)

add_library(ipsec SHARED IMPORTED)
set_target_properties(ipsec PROPERTIES
    IMPORTED_LOCATION ${CMAKE_CURRENT_SOURCE_DIR}/../jniLibs/${ANDROID_ABI}/libipsec.so)

add_library(androidbridge SHARED IMPORTED)
set_target_properties(androidbridge PROPERTIES
    IMPORTED_LOCATION ${CMAKE_CURRENT_SOURCE_DIR}/../jniLibs/${ANDROID_ABI}/libandroidbridge.so)

# 添加 OpenSSL 库
add_library(crypto STATIC IMPORTED)
set_target_properties(crypto PROPERTIES
    IMPORTED_LOCATION ${CMAKE_CURRENT_SOURCE_DIR}/../jniLibs/${ANDROID_ABI}/libcrypto_static.a)

add_library(ssl STATIC IMPORTED)
set_target_properties(ssl PROPERTIES
    IMPORTED_LOCATION ${CMAKE_CURRENT_SOURCE_DIR}/../jniLibs/${ANDROID_ABI}/libssl_static.a)

# 链接库
target_link_libraries(strongswan_integration
    strongswan
    charon
    ipsec
    androidbridge
    crypto
    ssl
    log
    android
    jnigraphics
)

# 设置编译选项
target_compile_definitions(strongswan_integration PRIVATE
    ANDROID
    STRONGSWAN_ANDROID
)

# 设置包含目录
target_include_directories(strongswan_integration PRIVATE
    ${CMAKE_CURRENT_SOURCE_DIR}/include
    ${CMAKE_CURRENT_SOURCE_DIR}/include/strongswan
    ${CMAKE_CURRENT_SOURCE_DIR}/include/charon
    ${CMAKE_CURRENT_SOURCE_DIR}/include/ipsec
)
