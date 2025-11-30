

https://live.european-language-grid.eu/catalogue/corpus/7564/download/


Description of the .json format:





Date: publication date of the article
URL: URL of the website

A maximum of three false statements are provided:
False_Statement_[1-3]_Location: Location of the verified false statement - Title, Teaser or Text
False_Statement_[1-3]_Index: The index numbers refer to the token (!) position / number. We tokenized the text with "spaCy" (the free open-source library for Python). 
Example: 
Title of Text: "The quick brown fox jumped over the lazy dog. The fox broke both his legs while jumping."
False_Statement: The fox broke both his legs while jumping.  
"False_Statement_1_Location": "Title",
"False_Statement_1_Index": "11-19"
 


Ratio_of_Fake_Statements: Percentage of fake found in the article 
1 = Text is based on true information. Up to 25% of the information in the text is false
2 = Up to 50% of the information in the text is false. The other statements in the article are factually accurate
3 = Up to 75% of the content non-factual and incorrect
4 = Pure fabrication with up to 100% false information in text 
9 = Unclear, unverifiable

Overall_Rating of the disinformation in text: range [0.1:1.0].
0.1 no disinformation in text 
0.2
0.3
0.4
0.5 neutral / ambivalent 
0.6
0.7
0.8
0.9
1.0 strong disinformative text
 
======================================================================
The original sources retain the copyright of the data.

You are allowed to use this dataset for research purposes only.

For more question about the dataset, please contact:
Inna Vogel, inna.vogel@sit.fraunhofer.de 

v1.01/09/2019

