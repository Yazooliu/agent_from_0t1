#!/usr/bin/env python
# -*- coding: UTF-8 -*-
"""=================================================
@PROJECT_NAME: agent_example
@File    : cli_main.py
@Author  : Liuyz
@Date    : 2024/6/28 14:04
@Function: 
    从0到1实现agent
@Modify History:
         
@Copyright：Copyright(c) 2024-2026. All Rights Reserved
=================================================="""
import time
from tools import tools_map
from prompt import gen_prompt, user_prompt
from model_provider import ModelProvider
from dotenv import load_dotenv
load_dotenv()
# agent 入口
"""todo"""
# 1、环境变量的设置
# 2、工具的引入
# 3、prompt模板
# 4、模型的初始化

mp = ModelProvider()


def parse_thoughts(response):
    try:
        thoughts = response.get("thoughts")
        observation = response.get("observation")
        plan = thoughts.get("plan")
        reasoning = thoughts.get("reasoning")
        criticism = thoughts.get("criticism")
        # observation = thoughts.get("speak")
        prompt = f"plan: {plan}\nreasoning: {reasoning}\ncriticism: {criticism}\nobservation: {observation}"
        return prompt
    except Exception as e:
        print("parse_thoughts error:{}".format(e))
        return "".format(e)


def agent_execute(query, max_request_time):
    cur_request_time = 0
    chat_history = []
    agent_scratch = ""
    while cur_request_time < max_request_time:
        cur_request_time += 1
        """
        如果返回结果满足预期则返回
        """
        """
        prompt包含的功能:
            1、任务的描述
            2、工具的描述
            3、用户的输入user_msg: 
            4、assistant_msg:
            5、结果的限制
            6、给出更好实践的描述
        """
        prompt = gen_prompt(query, agent_scratch)
        start_time = time.time()
        print('********* {}.开始调用大模型.....'.format(cur_request_time))
        end_time = time.time()
        """
        # call_llm
            1、sys_prompt
            2、user_prompt
            3、history
        """
        response = mp.chat(prompt, chat_history)
        print('结束调用{}次,花费时间:{}'.format(cur_request_time, end_time-start_time))

        # 大模型输出结果的处理
        if not response or not isinstance(response, dict):
            print("call llm exception, response is :{}".format(response))
            continue
        """
        response: 
        {
            "action": {
                "name": "action_name",
                "args": {
                    "args name": "args value"
                }
            },
            "thoughts":{
                "text": "thought",
                "plan": "plan",
                "criticism": "criticism",
                "speak": "当前步骤，返回给用户的总结",
                "reasoning": ""
            }
        }
        """
        # 这里统一叫tools #
        action_info = response.get("action")
        action_name = action_info.get("name")
        action_args = action_info.get("args")
        print("当前action_name:{}||action_入参:{}".format(action_name, action_args))
        # 其他输出信息
        thoughts = response.get("thoughts")
        plan = thoughts.get("plan")
        reasoning = thoughts.get("reasoning")
        criticism = thoughts.get("criticism")
        observation = thoughts.get("speak")
        print("observation:{}".format(observation))
        print("plan:{}".format(plan))
        print("reasoning:{}".format(reasoning))
        print("criticism:{}".format(criticism))
        if action_name == "finish":
            # 最终将结果返回给用户
            final_answer = action_args.get("answer")
            print("final_answer:{}".format(final_answer))
            break
        # speak
        observation = response.get("observation")
        try:
            """action-name到函数的映射 map -> {"action_name":func}"""
            # tools_map = {}
            # 获得函数然后直接调用,获得函数的结果
            func = tools_map.get(action_name)
            call_function_result = func(**action_args)
        except Exception as e:
            print("调用工具异常:{}".format(e))
            call_function_result = "{}".format(e)

        agent_scratch = agent_scratch + "\n: observation:{}\n execute action result: {}".format(observation,
                                                                                                call_function_result)
        # 从response 中拿出来想要用的信息
        assistant_msg = parse_thoughts(response)
        chat_history.append([user_prompt, assistant_msg])

    if cur_request_time == max_request_time:
        print("本次任务执行失败!")
    else:
        print("本次任务成功！")


def main():
    """支持用户的多次需要输入和交互"""
    max_request_time = 10
    while True:
        query = input("请输入您的目标:")
        if query == "exit":
            return
        agent_execute(query, max_request_time=max_request_time)


if __name__ == '__main__':
    # input = "请为我制定一个理财计划"
    main()
