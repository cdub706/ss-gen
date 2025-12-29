from textnode import TextNode, TextType
from htmlnode import HTMLNode

def main():
    node = TextNode("This is some anchor text", TextType.LINK, "https://www.boot.dev")
    print(node)

    node1 = HTMLNode("p", "This is a paragrapgh")
    print(node1)

if __name__ == "__main__":
    main()