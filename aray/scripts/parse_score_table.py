#!/usr/bin/env python3
# parse the score table

# %%
import json
from bs4 import BeautifulSoup

html = '''
<!DOCTYPE HTML>
<html>
<head>
    <title>Problems</title>
    <link rel="stylesheet" href="/assets/style.css">
</head>
<body>
    <header>
        <a href="https://icfpcontest2021.github.io/" target="_blank">ICFPC2021</a>
        <a href="/problems">problems</a>
        <a href="/teams">scores</a>
        <div class="session">
            <a href="/teams/bcf64d52-0d0f-4fee-8e21-5deb702997a1">OMG ICFP FTW</a>
        </div>
    </header>
    <h1>Problems</h1>
    <section>
        <table>
            <tr>
                <th>problem</th>
                <th>your dislikes</th>
                <th>minimal dislikes</th>
            </tr>
            <tr>
                <td>
                    <a href="/problems/1">1</a>
                </td>
                <td>3704</td>
                <td>624</td>
            </tr>
            <tr>
                <td>
                    <a href="/problems/2">2</a>
                </td>
                <td></td>
                <td>193</td>
            </tr>
            <tr>
                <td>
                    <a href="/problems/3">3</a>
                </td>
                <td></td>
                <td>186</td>
            </tr>
            <tr>
                <td>
                    <a href="/problems/4">4</a>
                </td>
                <td></td>
                <td>0</td>
            </tr>
            <tr>
                <td>
                    <a href="/problems/5">5</a>
                </td>
                <td></td>
                <td>45</td>
            </tr>
            <tr>
                <td>
                    <a href="/problems/6">6</a>
                </td>
                <td></td>
                <td>2663</td>
            </tr>
            <tr>
                <td>
                    <a href="/problems/7">7</a>
                </td>
                <td></td>
                <td>108</td>
            </tr>
            <tr>
                <td>
                    <a href="/problems/8">8</a>
                </td>
                <td></td>
                <td>1040</td>
            </tr>
            <tr>
                <td>
                    <a href="/problems/9">9</a>
                </td>
                <td></td>
                <td>779</td>
            </tr>
            <tr>
                <td>
                    <a href="/problems/10">10</a>
                </td>
                <td></td>
                <td>16</td>
            </tr>
            <tr>
                <td>
                    <a href="/problems/11">11</a>
                </td>
                <td>0</td>
                <td>0</td>
            </tr>
            <tr>
                <td>
                    <a href="/problems/12">12</a>
                </td>
                <td>0</td>
                <td>0</td>
            </tr>
            <tr>
                <td>
                    <a href="/problems/13">13</a>
                </td>
                <td>0</td>
                <td>0</td>
            </tr>
            <tr>
                <td>
                    <a href="/problems/14">14</a>
                </td>
                <td>116</td>
                <td>116</td>
            </tr>
            <tr>
                <td>
                    <a href="/problems/15">15</a>
                </td>
                <td>0</td>
                <td>0</td>
            </tr>
            <tr>
                <td>
                    <a href="/problems/16">16</a>
                </td>
                <td>0</td>
                <td>0</td>
            </tr>
            <tr>
                <td>
                    <a href="/problems/17">17</a>
                </td>
                <td>0</td>
                <td>0</td>
            </tr>
            <tr>
                <td>
                    <a href="/problems/18">18</a>
                </td>
                <td>0</td>
                <td>0</td>
            </tr>
            <tr>
                <td>
                    <a href="/problems/19">19</a>
                </td>
                <td>5318</td>
                <td>5318</td>
            </tr>
            <tr>
                <td>
                    <a href="/problems/20">20</a>
                </td>
                <td>0</td>
                <td>0</td>
            </tr>
            <tr>
                <td>
                    <a href="/problems/21">21</a>
                </td>
                <td>108</td>
                <td>0</td>
            </tr>
            <tr>
                <td>
                    <a href="/problems/22">22</a>
                </td>
                <td>0</td>
                <td>0</td>
            </tr>
            <tr>
                <td>
                    <a href="/problems/23">23</a>
                </td>
                <td>0</td>
                <td>0</td>
            </tr>
            <tr>
                <td>
                    <a href="/problems/24">24</a>
                </td>
                <td>136</td>
                <td>0</td>
            </tr>
            <tr>
                <td>
                    <a href="/problems/25">25</a>
                </td>
                <td></td>
                <td>0</td>
            </tr>
            <tr>
                <td>
                    <a href="/problems/26">26</a>
                </td>
                <td></td>
                <td>0</td>
            </tr>
            <tr>
                <td>
                    <a href="/problems/27">27</a>
                </td>
                <td>2423</td>
                <td>2423</td>
            </tr>
            <tr>
                <td>
                    <a href="/problems/28">28</a>
                </td>
                <td>3216</td>
                <td>3216</td>
            </tr>
            <tr>
                <td>
                    <a href="/problems/29">29</a>
                </td>
                <td>3114</td>
                <td>3114</td>
            </tr>
            <tr>
                <td>
                    <a href="/problems/30">30</a>
                </td>
                <td>1937</td>
                <td>1837</td>
            </tr>
            <tr>
                <td>
                    <a href="/problems/31">31</a>
                </td>
                <td></td>
                <td>10457</td>
            </tr>
            <tr>
                <td>
                    <a href="/problems/32">32</a>
                </td>
                <td>1894</td>
                <td>1894</td>
            </tr>
            <tr>
                <td>
                    <a href="/problems/33">33</a>
                </td>
                <td>3776</td>
                <td>2362</td>
            </tr>
            <tr>
                <td>
                    <a href="/problems/34">34</a>
                </td>
                <td></td>
                <td>0</td>
            </tr>
            <tr>
                <td>
                    <a href="/problems/35">35</a>
                </td>
                <td></td>
                <td>0</td>
            </tr>
            <tr>
                <td>
                    <a href="/problems/36">36</a>
                </td>
                <td>1463</td>
                <td>1444</td>
            </tr>
            <tr>
                <td>
                    <a href="/problems/37">37</a>
                </td>
                <td>2275</td>
                <td>1683</td>
            </tr>
            <tr>
                <td>
                    <a href="/problems/38">38</a>
                </td>
                <td></td>
                <td>0</td>
            </tr>
            <tr>
                <td>
                    <a href="/problems/39">39</a>
                </td>
                <td></td>
                <td>0</td>
            </tr>
            <tr>
                <td>
                    <a href="/problems/40">40</a>
                </td>
                <td></td>
                <td>3768</td>
            </tr>
            <tr>
                <td>
                    <a href="/problems/41">41</a>
                </td>
                <td>226</td>
                <td>0</td>
            </tr>
            <tr>
                <td>
                    <a href="/problems/42">42</a>
                </td>
                <td>2219</td>
                <td>1655</td>
            </tr>
            <tr>
                <td>
                    <a href="/problems/43">43</a>
                </td>
                <td></td>
                <td>0</td>
            </tr>
            <tr>
                <td>
                    <a href="/problems/44">44</a>
                </td>
                <td></td>
                <td>8706</td>
            </tr>
            <tr>
                <td>
                    <a href="/problems/45">45</a>
                </td>
                <td></td>
                <td>6379</td>
            </tr>
            <tr>
                <td>
                    <a href="/problems/46">46</a>
                </td>
                <td></td>
                <td>0</td>
            </tr>
            <tr>
                <td>
                    <a href="/problems/47">47</a>
                </td>
                <td></td>
                <td>0</td>
            </tr>
            <tr>
                <td>
                    <a href="/problems/48">48</a>
                </td>
                <td></td>
                <td>3617</td>
            </tr>
            <tr>
                <td>
                    <a href="/problems/49">49</a>
                </td>
                <td>153</td>
                <td>0</td>
            </tr>
            <tr>
                <td>
                    <a href="/problems/50">50</a>
                </td>
                <td></td>
                <td>3299</td>
            </tr>
            <tr>
                <td>
                    <a href="/problems/51">51</a>
                </td>
                <td></td>
                <td>0</td>
            </tr>
            <tr>
                <td>
                    <a href="/problems/52">52</a>
                </td>
                <td></td>
                <td>0</td>
            </tr>
            <tr>
                <td>
                    <a href="/problems/53">53</a>
                </td>
                <td></td>
                <td>0</td>
            </tr>
            <tr>
                <td>
                    <a href="/problems/54">54</a>
                </td>
                <td></td>
                <td>0</td>
            </tr>
            <tr>
                <td>
                    <a href="/problems/55">55</a>
                </td>
                <td></td>
                <td>0</td>
            </tr>
            <tr>
                <td>
                    <a href="/problems/56">56</a>
                </td>
                <td></td>
                <td>3021</td>
            </tr>
            <tr>
                <td>
                    <a href="/problems/57">57</a>
                </td>
                <td></td>
                <td>4514</td>
            </tr>
            <tr>
                <td>
                    <a href="/problems/58">58</a>
                </td>
                <td></td>
                <td>2171</td>
            </tr>
            <tr>
                <td>
                    <a href="/problems/59">59</a>
                </td>
                <td></td>
                <td>0</td>
            </tr>
            <tr>
                <td>
                    <a href="/problems/60">60</a>
                </td>
                <td></td>
                <td>211</td>
            </tr>
            <tr>
                <td>
                    <a href="/problems/61">61</a>
                </td>
                <td></td>
                <td>12587</td>
            </tr>
            <tr>
                <td>
                    <a href="/problems/62">62</a>
                </td>
                <td></td>
                <td>4156</td>
            </tr>
            <tr>
                <td>
                    <a href="/problems/63">63</a>
                </td>
                <td></td>
                <td>0</td>
            </tr>
            <tr>
                <td>
                    <a href="/problems/64">64</a>
                </td>
                <td></td>
                <td>0</td>
            </tr>
            <tr>
                <td>
                    <a href="/problems/65">65</a>
                </td>
                <td></td>
                <td>0</td>
            </tr>
            <tr>
                <td>
                    <a href="/problems/66">66</a>
                </td>
                <td></td>
                <td>7585</td>
            </tr>
            <tr>
                <td>
                    <a href="/problems/67">67</a>
                </td>
                <td>315</td>
                <td>0</td>
            </tr>
            <tr>
                <td>
                    <a href="/problems/68">68</a>
                </td>
                <td></td>
                <td>0</td>
            </tr>
            <tr>
                <td>
                    <a href="/problems/69">69</a>
                </td>
                <td></td>
                <td>705</td>
            </tr>
            <tr>
                <td>
                    <a href="/problems/70">70</a>
                </td>
                <td></td>
                <td>0</td>
            </tr>
            <tr>
                <td>
                    <a href="/problems/71">71</a>
                </td>
                <td></td>
                <td>5230</td>
            </tr>
            <tr>
                <td>
                    <a href="/problems/72">72</a>
                </td>
                <td></td>
                <td>0</td>
            </tr>
            <tr>
                <td>
                    <a href="/problems/73">73</a>
                </td>
                <td></td>
                <td>0</td>
            </tr>
            <tr>
                <td>
                    <a href="/problems/74">74</a>
                </td>
                <td></td>
                <td>2383</td>
            </tr>
            <tr>
                <td>
                    <a href="/problems/75">75</a>
                </td>
                <td></td>
                <td>0</td>
            </tr>
            <tr>
                <td>
                    <a href="/problems/76">76</a>
                </td>
                <td></td>
                <td>0</td>
            </tr>
            <tr>
                <td>
                    <a href="/problems/77">77</a>
                </td>
                <td></td>
                <td>0</td>
            </tr>
            <tr>
                <td>
                    <a href="/problems/78">78</a>
                </td>
                <td></td>
                <td>179</td>
            </tr>
            <tr>
                <td>
                    <a href="/problems/79">79</a>
                </td>
                <td></td>
                <td>21290</td>
            </tr>
            <tr>
                <td>
                    <a href="/problems/80">80</a>
                </td>
                <td></td>
                <td>0</td>
            </tr>
            <tr>
                <td>
                    <a href="/problems/81">81</a>
                </td>
                <td></td>
                <td>0</td>
            </tr>
            <tr>
                <td>
                    <a href="/problems/82">82</a>
                </td>
                <td></td>
                <td>1451</td>
            </tr>
            <tr>
                <td>
                    <a href="/problems/83">83</a>
                </td>
                <td></td>
                <td>5251</td>
            </tr>
            <tr>
                <td>
                    <a href="/problems/84">84</a>
                </td>
                <td></td>
                <td>0</td>
            </tr>
            <tr>
                <td>
                    <a href="/problems/85">85</a>
                </td>
                <td></td>
                <td>0</td>
            </tr>
            <tr>
                <td>
                    <a href="/problems/86">86</a>
                </td>
                <td></td>
                <td>5354</td>
            </tr>
            <tr>
                <td>
                    <a href="/problems/87">87</a>
                </td>
                <td></td>
                <td>5267</td>
            </tr>
            <tr>
                <td>
                    <a href="/problems/88">88</a>
                </td>
                <td></td>
                <td>9908</td>
            </tr>
            <tr>
                <td>
                    <a href="/problems/89">89</a>
                </td>
                <td></td>
                <td>85224</td>
            </tr>
            <tr>
                <td>
                    <a href="/problems/90">90</a>
                </td>
                <td></td>
                <td>0</td>
            </tr>
            <tr>
                <td>
                    <a href="/problems/91">91</a>
                </td>
                <td></td>
                <td>12879</td>
            </tr>
            <tr>
                <td>
                    <a href="/problems/92">92</a>
                </td>
                <td></td>
                <td>37958</td>
            </tr>
            <tr>
                <td>
                    <a href="/problems/93">93</a>
                </td>
                <td></td>
                <td>0</td>
            </tr>
            <tr>
                <td>
                    <a href="/problems/94">94</a>
                </td>
                <td></td>
                <td>1506</td>
            </tr>
            <tr>
                <td>
                    <a href="/problems/95">95</a>
                </td>
                <td></td>
                <td>5744</td>
            </tr>
            <tr>
                <td>
                    <a href="/problems/96">96</a>
                </td>
                <td></td>
                <td>14461</td>
            </tr>
            <tr>
                <td>
                    <a href="/problems/97">97</a>
                </td>
                <td></td>
                <td>0</td>
            </tr>
            <tr>
                <td>
                    <a href="/problems/98">98</a>
                </td>
                <td></td>
                <td>29886</td>
            </tr>
            <tr>
                <td>
                    <a href="/problems/99">99</a>
                </td>
                <td></td>
                <td>7246</td>
            </tr>
            <tr>
                <td>
                    <a href="/problems/100">100</a>
                </td>
                <td></td>
                <td>5425</td>
            </tr>
            <tr>
                <td>
                    <a href="/problems/101">101</a>
                </td>
                <td></td>
                <td>7581</td>
            </tr>
            <tr>
                <td>
                    <a href="/problems/102">102</a>
                </td>
                <td></td>
                <td>62355</td>
            </tr>
            <tr>
                <td>
                    <a href="/problems/103">103</a>
                </td>
                <td></td>
                <td>49921</td>
            </tr>
            <tr>
                <td>
                    <a href="/problems/104">104</a>
                </td>
                <td></td>
                <td>15872</td>
            </tr>
            <tr>
                <td>
                    <a href="/problems/105">105</a>
                </td>
                <td></td>
                <td>7</td>
            </tr>
            <tr>
                <td>
                    <a href="/problems/106">106</a>
                </td>
                <td></td>
                <td>0</td>
            </tr>
            <tr>
                <td>
                    <a href="/problems/107">107</a>
                </td>
                <td></td>
                <td>4511</td>
            </tr>
            <tr>
                <td>
                    <a href="/problems/108">108</a>
                </td>
                <td></td>
                <td>18274</td>
            </tr>
            <tr>
                <td>
                    <a href="/problems/109">109</a>
                </td>
                <td></td>
                <td>376</td>
            </tr>
            <tr>
                <td>
                    <a href="/problems/110">110</a>
                </td>
                <td></td>
                <td>12386</td>
            </tr>
            <tr>
                <td>
                    <a href="/problems/111">111</a>
                </td>
                <td></td>
                <td>15564</td>
            </tr>
            <tr>
                <td>
                    <a href="/problems/112">112</a>
                </td>
                <td></td>
                <td>20277</td>
            </tr>
            <tr>
                <td>
                    <a href="/problems/113">113</a>
                </td>
                <td></td>
                <td>10892</td>
            </tr>
            <tr>
                <td>
                    <a href="/problems/114">114</a>
                </td>
                <td></td>
                <td>1170</td>
            </tr>
            <tr>
                <td>
                    <a href="/problems/115">115</a>
                </td>
                <td></td>
                <td>46985</td>
            </tr>
            <tr>
                <td>
                    <a href="/problems/116">116</a>
                </td>
                <td></td>
                <td>4458</td>
            </tr>
            <tr>
                <td>
                    <a href="/problems/117">117</a>
                </td>
                <td></td>
                <td>28703</td>
            </tr>
            <tr>
                <td>
                    <a href="/problems/118">118</a>
                </td>
                <td></td>
                <td>4567</td>
            </tr>
            <tr>
                <td>
                    <a href="/problems/119">119</a>
                </td>
                <td></td>
                <td>22819</td>
            </tr>
            <tr>
                <td>
                    <a href="/problems/120">120</a>
                </td>
                <td></td>
                <td>20237</td>
            </tr>
            <tr>
                <td>
                    <a href="/problems/121">121</a>
                </td>
                <td></td>
                <td>12349</td>
            </tr>
            <tr>
                <td>
                    <a href="/problems/122">122</a>
                </td>
                <td></td>
                <td>117</td>
            </tr>
            <tr>
                <td>
                    <a href="/problems/123">123</a>
                </td>
                <td></td>
                <td>13534</td>
            </tr>
            <tr>
                <td>
                    <a href="/problems/124">124</a>
                </td>
                <td></td>
                <td>15855</td>
            </tr>
            <tr>
                <td>
                    <a href="/problems/125">125</a>
                </td>
                <td></td>
                <td>492</td>
            </tr>
            <tr>
                <td>
                    <a href="/problems/126">126</a>
                </td>
                <td></td>
                <td>11952</td>
            </tr>
            <tr>
                <td>
                    <a href="/problems/127">127</a>
                </td>
                <td></td>
                <td>17227</td>
            </tr>
            <tr>
                <td>
                    <a href="/problems/128">128</a>
                </td>
                <td></td>
                <td>12247</td>
            </tr>
            <tr>
                <td>
                    <a href="/problems/129">129</a>
                </td>
                <td></td>
                <td>10688</td>
            </tr>
            <tr>
                <td>
                    <a href="/problems/130">130</a>
                </td>
                <td></td>
                <td>6612</td>
            </tr>
            <tr>
                <td>
                    <a href="/problems/131">131</a>
                </td>
                <td></td>
                <td>18812</td>
            </tr>
            <tr>
                <td>
                    <a href="/problems/132">132</a>
                </td>
                <td></td>
                <td>15583</td>
            </tr>
        </table>
    </section>
    <footer>
        cloud hosting provided by 
        <a href="https://fugue.co/">fugue</a>
         | version ca545e81
    </footer>
</body>
</html>
'''
# parse the html
soup = BeautifulSoup(html, 'html.parser')
# find all the table
tables = soup.find_all('table')
# get the first table
table = tables[0]
# get the rows of the table as lists
rows = table.find_all('tr')
# process the rows into strings of data
data = []
for row in rows:
    data.append([None if val.text == '' else int(val.text) for val in row.find_all('td')])
data
# process into a dict of dicts
scores = {}
for row in data:
    if row == []:
        continue
    problem_number = row[0]
    our_score = row[1]
    best_score = row[2]
    assert problem_number not in scores
    scores[problem_number] = {
        'problem_number': problem_number,
        'our_score': our_score,
        'best_score': best_score,
    }
# write to json file
with open('/tmp/scores.json', 'w') as f:
    json.dump(scores, f)
