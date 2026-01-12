#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
视频API测试器
测试分析出的API端点，尝试获取实际的视频信息
"""

import requests
import json
import time
from urllib.parse import urlparse
from typing import Dict, List, Any, Optional


class VideoAPITester:
    """视频API测试器"""
    
    def __init__(self):
        """初始化测试器"""
        self.session = requests.Session()
        self._setup_session()
        self.results = []
    
    def _setup_session(self):
        """设置请求会话"""
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'application/json, text/plain, */*',
            'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
            'Referer': 'https://www.a3m5m.com/',
        })
    
    def test_api_endpoints(self, analysis_file: str) -> Dict[str, Any]:
        """
        测试API端点
        
        Args:
            analysis_file: 分析结果JSON文件路径
            
        Returns:
            测试结果
        """
        print(f"🔍 测试API端点: {analysis_file}")
        print("=" * 60)
        
        try:
            with open(analysis_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
        except Exception as e:
            print(f"❌ 读取文件失败: {e}")
            return {'error': str(e)}
        
        result = {
            'base_url': data.get('base_url', ''),
            'tested_endpoints': [],
            'successful_endpoints': [],
            'video_info_found': [],
            'test_summary': {}
        }
        
        # 获取API端点
        api_endpoints = data.get('api_endpoints', [])
        
        # 测试前10个API端点
        for i, endpoint in enumerate(api_endpoints[:10], 1):
            print(f"\n🔗 测试API端点 {i}: {endpoint['url']}")
            
            test_result = self._test_single_endpoint(endpoint)
            result['tested_endpoints'].append(test_result)
            
            if test_result['success']:
                result['successful_endpoints'].append(test_result)
                
                # 检查是否包含视频信息
                if self._contains_video_info(test_result['response']):
                    result['video_info_found'].append(test_result)
                    print(f"  ✅ 发现视频信息!")
        
        # 生成测试摘要
        result['test_summary'] = self._generate_test_summary(result)
        
        return result
    
    def _test_single_endpoint(self, endpoint: Dict[str, Any]) -> Dict[str, Any]:
        """测试单个API端点"""
        url = endpoint['url']
        result = {
            'url': url,
            'type': endpoint['type'],
            'success': False,
            'status_code': None,
            'response': None,
            'error': None,
            'response_time': 0
        }
        
        try:
            start_time = time.time()
            
            # 尝试GET请求
            response = self.session.get(url, timeout=10)
            result['status_code'] = response.status_code
            result['response_time'] = time.time() - start_time
            
            if response.status_code == 200:
                result['success'] = True
                try:
                    # 尝试解析JSON
                    result['response'] = response.json()
                except:
                    # 如果不是JSON，保存文本内容
                    result['response'] = response.text[:1000]  # 限制长度
            else:
                result['error'] = f"HTTP {response.status_code}"
                
        except requests.exceptions.Timeout:
            result['error'] = "请求超时"
        except requests.exceptions.ConnectionError:
            result['error'] = "连接错误"
        except Exception as e:
            result['error'] = str(e)
        
        # 打印结果
        if result['success']:
            print(f"  ✅ 成功 (状态码: {result['status_code']}, 响应时间: {result['response_time']:.2f}s)")
        else:
            print(f"  ❌ 失败: {result['error']}")
        
        return result
    
    def _contains_video_info(self, response: Any) -> bool:
        """检查响应是否包含视频信息"""
        if not response:
            return False
        
        # 如果是字符串，转换为小写检查
        if isinstance(response, str):
            response_lower = response.lower()
        else:
            # 如果是字典，转换为JSON字符串检查
            response_lower = json.dumps(response, ensure_ascii=False).lower()
        
        # 检查视频相关关键词
        video_keywords = [
            'video', 'mp4', 'm3u8', 'stream', 'play', 'url', 'src',
            'hls', 'dash', 'ts', 'webm', 'ogg', 'avi', 'mov',
            'title', 'duration', 'quality', 'resolution', 'bitrate'
        ]
        
        return any(keyword in response_lower for keyword in video_keywords)
    
    def _generate_test_summary(self, result: Dict[str, Any]) -> Dict[str, Any]:
        """生成测试摘要"""
        summary = {
            'total_tested': len(result['tested_endpoints']),
            'successful': len(result['successful_endpoints']),
            'failed': len(result['tested_endpoints']) - len(result['successful_endpoints']),
            'video_info_found': len(result['video_info_found']),
            'success_rate': 0,
            'top_endpoints': []
        }
        
        if summary['total_tested'] > 0:
            summary['success_rate'] = (summary['successful'] / summary['total_tested']) * 100
        
        # 获取前5个成功的端点
        summary['top_endpoints'] = result['successful_endpoints'][:5]
        
        return summary
    
    def test_video_data_endpoints(self, base_url: str) -> Dict[str, Any]:
        """测试视频数据端点"""
        print(f"\n🎬 测试视频数据端点: {base_url}")
        print("-" * 40)
        
        # 构建可能的视频数据端点
        video_id = base_url.split('/')[-1]  # 提取视频ID
        possible_endpoints = [
            f"{base_url}/data",
            f"{base_url}/info",
            f"{base_url}/details",
            f"{base_url}/api/video/{video_id}",
            f"{base_url}/api/data/{video_id}",
            f"{base_url}/api/info/{video_id}",
            f"{base_url}/api/details/{video_id}",
            f"{base_url}/api/play/{video_id}",
            f"{base_url}/api/stream/{video_id}",
            f"{base_url}/api/media/{video_id}",
        ]
        
        result = {
            'base_url': base_url,
            'video_id': video_id,
            'tested_endpoints': [],
            'successful_endpoints': [],
            'video_info_found': []
        }
        
        for i, endpoint in enumerate(possible_endpoints, 1):
            print(f"\n🔗 测试端点 {i}: {endpoint}")
            
            test_result = self._test_single_endpoint({
                'url': endpoint,
                'type': 'video_data'
            })
            result['tested_endpoints'].append(test_result)
            
            if test_result['success']:
                result['successful_endpoints'].append(test_result)
                
                if self._contains_video_info(test_result['response']):
                    result['video_info_found'].append(test_result)
                    print(f"  ✅ 发现视频信息!")
        
        return result
    
    def save_test_results(self, result: Dict[str, Any], filename: str = None) -> str:
        """保存测试结果"""
        if not filename:
            domain = urlparse(result['base_url']).netloc
            timestamp = int(time.time())
            filename = f"video_api_test_{domain}_{timestamp}.json"
        
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(result, f, ensure_ascii=False, indent=2)
            
            print(f"✅ 测试结果已保存到: {filename}")
            return filename
        except Exception as e:
            print(f"❌ 保存失败: {e}")
            return ""


def main():
    """主函数"""
    print("视频API测试器")
    print("=" * 60)
    
    # 分析结果文件
    analysis_file = "video_analysis_www.a3m5m.com_1759163634.json"
    base_url = "https://www.a3m5m.com/s/video/shipin/1044455"
    
    # 创建测试器
    tester = VideoAPITester()
    
    # 测试API端点
    result = tester.test_api_endpoints(analysis_file)
    
    if 'error' not in result:
        print(f"\n🎉 API端点测试完成!")
        
        # 显示测试摘要
        summary = result['test_summary']
        print(f"\n📊 测试摘要:")
        print(f"  总测试数: {summary['total_tested']}")
        print(f"  成功数: {summary['successful']}")
        print(f"  失败数: {summary['failed']}")
        print(f"  发现视频信息: {summary['video_info_found']}")
        print(f"  成功率: {summary['success_rate']:.1f}%")
        
        # 显示成功的端点
        if result['successful_endpoints']:
            print(f"\n✅ 成功的端点:")
            for i, endpoint in enumerate(result['successful_endpoints'], 1):
                print(f"  {i}. {endpoint['url']}")
                print(f"     状态码: {endpoint['status_code']}, 响应时间: {endpoint['response_time']:.2f}s")
        
        # 显示发现视频信息的端点
        if result['video_info_found']:
            print(f"\n🎬 发现视频信息的端点:")
            for i, endpoint in enumerate(result['video_info_found'], 1):
                print(f"  {i}. {endpoint['url']}")
                print(f"     响应: {str(endpoint['response'])[:200]}...")
        
        # 保存测试结果
        filename = tester.save_test_results(result)
        
        # 测试视频数据端点
        print(f"\n" + "=" * 60)
        video_data_result = tester.test_video_data_endpoints(base_url)
        
        if video_data_result['successful_endpoints']:
            print(f"\n✅ 视频数据端点测试成功:")
            for endpoint in video_data_result['successful_endpoints']:
                print(f"  - {endpoint['url']}")
                print(f"    响应: {str(endpoint['response'])[:200]}...")
        
        # 保存视频数据测试结果
        video_data_filename = tester.save_test_results(video_data_result, "video_data_test_results.json")
        
    else:
        print(f"\n❌ 测试失败: {result['error']}")


if __name__ == "__main__":
    main()
