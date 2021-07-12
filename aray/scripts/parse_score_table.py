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
                <td>4551</td>
                <td>193</td>
            </tr>
            <tr>
                <td>
                    <a href="/problems/3">3</a>
                </td>
                <td>5319</td>
                <td>199</td>
            </tr>
            <tr>
                <td>
                    <a href="/problems/4">4</a>
                </td>
                <td>0</td>
                <td>0</td>
            </tr>
            <tr>
                <td>
                    <a href="/problems/5">5</a>
                </td>
                <td>3632</td>
                <td>29</td>
            </tr>
            <tr>
                <td>
                    <a href="/problems/6">6</a>
                </td>
                <td>25757</td>
                <td>2655</td>
            </tr>
            <tr>
                <td>
                    <a href="/problems/7">7</a>
                </td>
                <td>2001</td>
                <td>112</td>
            </tr>
            <tr>
                <td>
                    <a href="/problems/8">8</a>
                </td>
                <td>2311</td>
                <td>892</td>
            </tr>
            <tr>
                <td>
                    <a href="/problems/9">9</a>
                </td>
                <td>26431</td>
                <td>779</td>
            </tr>
            <tr>
                <td>
                    <a href="/problems/10">10</a>
                </td>
                <td>4211</td>
                <td>9</td>
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
                <td>0</td>
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
                <td>0</td>
                <td>0</td>
            </tr>
            <tr>
                <td>
                    <a href="/problems/25">25</a>
                </td>
                <td>0</td>
                <td>0</td>
            </tr>
            <tr>
                <td>
                    <a href="/problems/26">26</a>
                </td>
                <td>0</td>
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
                <td>1837</td>
                <td>1837</td>
            </tr>
            <tr>
                <td>
                    <a href="/problems/31">31</a>
                </td>
                <td>10457</td>
                <td>5025</td>
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
                <td>2362</td>
                <td>2362</td>
            </tr>
            <tr>
                <td>
                    <a href="/problems/34">34</a>
                </td>
                <td>0</td>
                <td>0</td>
            </tr>
            <tr>
                <td>
                    <a href="/problems/35">35</a>
                </td>
                <td>0</td>
                <td>0</td>
            </tr>
            <tr>
                <td>
                    <a href="/problems/36">36</a>
                </td>
                <td>1453</td>
                <td>1444</td>
            </tr>
            <tr>
                <td>
                    <a href="/problems/37">37</a>
                </td>
                <td>1683</td>
                <td>1683</td>
            </tr>
            <tr>
                <td>
                    <a href="/problems/38">38</a>
                </td>
                <td>0</td>
                <td>0</td>
            </tr>
            <tr>
                <td>
                    <a href="/problems/39">39</a>
                </td>
                <td>0</td>
                <td>0</td>
            </tr>
            <tr>
                <td>
                    <a href="/problems/40">40</a>
                </td>
                <td>6457</td>
                <td>3768</td>
            </tr>
            <tr>
                <td>
                    <a href="/problems/41">41</a>
                </td>
                <td>0</td>
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
                <td>0</td>
                <td>0</td>
            </tr>
            <tr>
                <td>
                    <a href="/problems/44">44</a>
                </td>
                <td>13436</td>
                <td>8706</td>
            </tr>
            <tr>
                <td>
                    <a href="/problems/45">45</a>
                </td>
                <td>8233</td>
                <td>6379</td>
            </tr>
            <tr>
                <td>
                    <a href="/problems/46">46</a>
                </td>
                <td>0</td>
                <td>0</td>
            </tr>
            <tr>
                <td>
                    <a href="/problems/47">47</a>
                </td>
                <td>0</td>
                <td>0</td>
            </tr>
            <tr>
                <td>
                    <a href="/problems/48">48</a>
                </td>
                <td>6802</td>
                <td>3617</td>
            </tr>
            <tr>
                <td>
                    <a href="/problems/49">49</a>
                </td>
                <td>0</td>
                <td>0</td>
            </tr>
            <tr>
                <td>
                    <a href="/problems/50">50</a>
                </td>
                <td>5515</td>
                <td>3299</td>
            </tr>
            <tr>
                <td>
                    <a href="/problems/51">51</a>
                </td>
                <td>0</td>
                <td>0</td>
            </tr>
            <tr>
                <td>
                    <a href="/problems/52">52</a>
                </td>
                <td>0</td>
                <td>0</td>
            </tr>
            <tr>
                <td>
                    <a href="/problems/53">53</a>
                </td>
                <td>0</td>
                <td>0</td>
            </tr>
            <tr>
                <td>
                    <a href="/problems/54">54</a>
                </td>
                <td>0</td>
                <td>0</td>
            </tr>
            <tr>
                <td>
                    <a href="/problems/55">55</a>
                </td>
                <td>3396</td>
                <td>0</td>
            </tr>
            <tr>
                <td>
                    <a href="/problems/56">56</a>
                </td>
                <td>12035</td>
                <td>3021</td>
            </tr>
            <tr>
                <td>
                    <a href="/problems/57">57</a>
                </td>
                <td>16840</td>
                <td>4293</td>
            </tr>
            <tr>
                <td>
                    <a href="/problems/58">58</a>
                </td>
                <td>5464</td>
                <td>2171</td>
            </tr>
            <tr>
                <td>
                    <a href="/problems/59">59</a>
                </td>
                <td>0</td>
                <td>0</td>
            </tr>
            <tr>
                <td>
                    <a href="/problems/60">60</a>
                </td>
                <td>5431</td>
                <td>211</td>
            </tr>
            <tr>
                <td>
                    <a href="/problems/61">61</a>
                </td>
                <td>31778</td>
                <td>12587</td>
            </tr>
            <tr>
                <td>
                    <a href="/problems/62">62</a>
                </td>
                <td>59652</td>
                <td>4156</td>
            </tr>
            <tr>
                <td>
                    <a href="/problems/63">63</a>
                </td>
                <td>0</td>
                <td>0</td>
            </tr>
            <tr>
                <td>
                    <a href="/problems/64">64</a>
                </td>
                <td>368000</td>
                <td>0</td>
            </tr>
            <tr>
                <td>
                    <a href="/problems/65">65</a>
                </td>
                <td>207110</td>
                <td>0</td>
            </tr>
            <tr>
                <td>
                    <a href="/problems/66">66</a>
                </td>
                <td>30154</td>
                <td>7585</td>
            </tr>
            <tr>
                <td>
                    <a href="/problems/67">67</a>
                </td>
                <td>300</td>
                <td>0</td>
            </tr>
            <tr>
                <td>
                    <a href="/problems/68">68</a>
                </td>
                <td>249292</td>
                <td>0</td>
            </tr>
            <tr>
                <td>
                    <a href="/problems/69">69</a>
                </td>
                <td>8675</td>
                <td>705</td>
            </tr>
            <tr>
                <td>
                    <a href="/problems/70">70</a>
                </td>
                <td>0</td>
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
                <td>5439</td>
                <td>0</td>
            </tr>
            <tr>
                <td>
                    <a href="/problems/73">73</a>
                </td>
                <td>0</td>
                <td>0</td>
            </tr>
            <tr>
                <td>
                    <a href="/problems/74">74</a>
                </td>
                <td>113729</td>
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
                <td>44996</td>
                <td>0</td>
            </tr>
            <tr>
                <td>
                    <a href="/problems/77">77</a>
                </td>
                <td>0</td>
                <td>0</td>
            </tr>
            <tr>
                <td>
                    <a href="/problems/78">78</a>
                </td>
                <td>35890</td>
                <td>149</td>
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
                <td>228149</td>
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
                <td>26943</td>
                <td>1243</td>
            </tr>
            <tr>
                <td>
                    <a href="/problems/83">83</a>
                </td>
                <td>74437</td>
                <td>3349</td>
            </tr>
            <tr>
                <td>
                    <a href="/problems/84">84</a>
                </td>
                <td>0</td>
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
                <td>98537</td>
                <td>5354</td>
            </tr>
            <tr>
                <td>
                    <a href="/problems/87">87</a>
                </td>
                <td></td>
                <td>4677</td>
            </tr>
            <tr>
                <td>
                    <a href="/problems/88">88</a>
                </td>
                <td>19391</td>
                <td>9908</td>
            </tr>
            <tr>
                <td>
                    <a href="/problems/89">89</a>
                </td>
                <td>366589</td>
                <td>82872</td>
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
                <td>242786</td>
                <td>12879</td>
            </tr>
            <tr>
                <td>
                    <a href="/problems/92">92</a>
                </td>
                <td>185064</td>
                <td>33754</td>
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
                <td>34748</td>
                <td>1506</td>
            </tr>
            <tr>
                <td>
                    <a href="/problems/95">95</a>
                </td>
                <td></td>
                <td>5281</td>
            </tr>
            <tr>
                <td>
                    <a href="/problems/96">96</a>
                </td>
                <td></td>
                <td>13834</td>
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
                <td>28409</td>
            </tr>
            <tr>
                <td>
                    <a href="/problems/99">99</a>
                </td>
                <td></td>
                <td>5887</td>
            </tr>
            <tr>
                <td>
                    <a href="/problems/100">100</a>
                </td>
                <td></td>
                <td>4193</td>
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
                <td>60220</td>
            </tr>
            <tr>
                <td>
                    <a href="/problems/103">103</a>
                </td>
                <td></td>
                <td>47952</td>
            </tr>
            <tr>
                <td>
                    <a href="/problems/104">104</a>
                </td>
                <td>❌</td>
                <td>14918</td>
            </tr>
            <tr>
                <td>
                    <a href="/problems/105">105</a>
                </td>
                <td></td>
                <td>0</td>
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
                <td>2786</td>
            </tr>
            <tr>
                <td>
                    <a href="/problems/108">108</a>
                </td>
                <td>191855</td>
                <td>18274</td>
            </tr>
            <tr>
                <td>
                    <a href="/problems/109">109</a>
                </td>
                <td>11106</td>
                <td>321</td>
            </tr>
            <tr>
                <td>
                    <a href="/problems/110">110</a>
                </td>
                <td>67682</td>
                <td>11833</td>
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
                <td>20164</td>
            </tr>
            <tr>
                <td>
                    <a href="/problems/113">113</a>
                </td>
                <td>121322</td>
                <td>9360</td>
            </tr>
            <tr>
                <td>
                    <a href="/problems/114">114</a>
                </td>
                <td></td>
                <td>0</td>
            </tr>
            <tr>
                <td>
                    <a href="/problems/115">115</a>
                </td>
                <td></td>
                <td>38408</td>
            </tr>
            <tr>
                <td>
                    <a href="/problems/116">116</a>
                </td>
                <td></td>
                <td>4099</td>
            </tr>
            <tr>
                <td>
                    <a href="/problems/117">117</a>
                </td>
                <td>86924</td>
                <td>28703</td>
            </tr>
            <tr>
                <td>
                    <a href="/problems/118">118</a>
                </td>
                <td>106303</td>
                <td>3781</td>
            </tr>
            <tr>
                <td>
                    <a href="/problems/119">119</a>
                </td>
                <td>303830</td>
                <td>18972</td>
            </tr>
            <tr>
                <td>
                    <a href="/problems/120">120</a>
                </td>
                <td>199308</td>
                <td>13391</td>
            </tr>
            <tr>
                <td>
                    <a href="/problems/121">121</a>
                </td>
                <td>92215</td>
                <td>11879</td>
            </tr>
            <tr>
                <td>
                    <a href="/problems/122">122</a>
                </td>
                <td></td>
                <td>0</td>
            </tr>
            <tr>
                <td>
                    <a href="/problems/123">123</a>
                </td>
                <td>230177</td>
                <td>13056</td>
            </tr>
            <tr>
                <td>
                    <a href="/problems/124">124</a>
                </td>
                <td></td>
                <td>14685</td>
            </tr>
            <tr>
                <td>
                    <a href="/problems/125">125</a>
                </td>
                <td>1552827</td>
                <td>0</td>
            </tr>
            <tr>
                <td>
                    <a href="/problems/126">126</a>
                </td>
                <td></td>
                <td>6077</td>
            </tr>
            <tr>
                <td>
                    <a href="/problems/127">127</a>
                </td>
                <td>26485</td>
                <td>16597</td>
            </tr>
            <tr>
                <td>
                    <a href="/problems/128">128</a>
                </td>
                <td></td>
                <td>9853</td>
            </tr>
            <tr>
                <td>
                    <a href="/problems/129">129</a>
                </td>
                <td></td>
                <td>7992</td>
            </tr>
            <tr>
                <td>
                    <a href="/problems/130">130</a>
                </td>
                <td>39965</td>
                <td>6470</td>
            </tr>
            <tr>
                <td>
                    <a href="/problems/131">131</a>
                </td>
                <td></td>
                <td>15748</td>
            </tr>
            <tr>
                <td>
                    <a href="/problems/132">132</a>
                </td>
                <td>❌</td>
                <td>14517</td>
            </tr>
        </table>
    </section>
    <footer>
        cloud hosting provided by 
        <a href="https://fugue.co/">fugue</a>
         | version c1e792b6
    </footer>
</body>
</html>



'''.replace('❌', '')
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


# %%
# get the list of problem_numbers that our score is currently missing
missing_scores = []
for i in range(1, 131):
    if i == 104:
        continue
    if scores[i]['our_score'] == None:
        missing_scores.append(i)
missing_scores

# %%
forbiddens_list = '''
/tmp/104-forbidden2.json
/tmp/108-forbidden2.json
/tmp/109-forbidden2.json
/tmp/10-forbidden2.json
/tmp/110-forbidden2.json
/tmp/113-forbidden2.json
/tmp/119-forbidden2.json
/tmp/11-forbidden2.json
/tmp/120-forbidden2.json
/tmp/123-forbidden2.json
/tmp/127-forbidden2.json
/tmp/12-forbidden2.json
/tmp/130-forbidden2.json
/tmp/132-forbidden2.json
/tmp/13-forbidden2.json
/tmp/14-forbidden2.json
/tmp/15-forbidden2.json
/tmp/16-forbidden2.json
/tmp/17-forbidden2.json
/tmp/18-forbidden2.json
/tmp/19-forbidden2.json
/tmp/1-forbidden2.json
/tmp/20-forbidden2.json
/tmp/21-forbidden2.json
/tmp/22-forbidden2.json
/tmp/23-forbidden2.json
/tmp/24-forbidden2.json
/tmp/25-forbidden2.json
/tmp/26-forbidden2.json
/tmp/27-forbidden2.json
/tmp/28-forbidden2.json
/tmp/29-forbidden2.json
/tmp/2-forbidden2.json
/tmp/30-forbidden2.json
/tmp/31-forbidden2.json
/tmp/32-forbidden2.json
/tmp/33-forbidden2.json
/tmp/34-forbidden2.json
/tmp/35-forbidden2.json
/tmp/36-forbidden2.json
/tmp/37-forbidden2.json
/tmp/38-forbidden2.json
/tmp/39-forbidden2.json
/tmp/3-forbidden2.json
/tmp/40-forbidden2.json
/tmp/41-forbidden2.json
/tmp/42-forbidden2.json
/tmp/43-forbidden2.json
/tmp/44-forbidden2.json
/tmp/45-forbidden2.json
/tmp/46-forbidden2.json
/tmp/47-forbidden2.json
/tmp/48-forbidden2.json
/tmp/49-forbidden2.json
/tmp/4-forbidden2.json
/tmp/50-forbidden2.json
/tmp/51-forbidden2.json
/tmp/52-forbidden2.json
/tmp/53-forbidden2.json
/tmp/54-forbidden2.json
/tmp/55-forbidden2.json
/tmp/56-forbidden2.json
/tmp/57-forbidden2.json
/tmp/58-forbidden2.json
/tmp/59-forbidden2.json
/tmp/5-forbidden2.json
/tmp/60-forbidden2.json
/tmp/61-forbidden2.json
/tmp/63-forbidden2.json
/tmp/66-forbidden2.json
/tmp/67-forbidden2.json
/tmp/69-forbidden2.json
/tmp/6-forbidden2.json
/tmp/70-forbidden2.json
/tmp/73-forbidden2.json
/tmp/77-forbidden2.json
/tmp/7-forbidden2.json
/tmp/81-forbidden2.json
/tmp/84-forbidden2.json
/tmp/86-forbidden2.json
/tmp/88-forbidden2.json
/tmp/89-forbidden2.json
/tmp/8-forbidden2.json
/tmp/91-forbidden2.json
/tmp/92-forbidden2.json
/tmp/94-forbidden2.json
'''.strip().split()
forbidden_numbers = [int(x[5:].split('-')[0]) for x in forbiddens_list]
forbidden_numbers

# %%
ns = sorted(i for i in forbidden_numbers if i in missing_scores)
' '.join(str(i) for i in ns)

# %%
# bash command to run these
for x in ns:
    print(f'python gosh_dangit_its_them_ortools_boys_again/edgy.py {x} --timeout 10000.0 &')
