"""
HTML Node Tree Structure

This module defines a tree-based representation of HTML documents. HTMLNodes
can be composed to build complex HTML structures that are then converted to
HTML strings. This abstraction allows for programmatic HTML generation with
proper nesting and attribute handling.

The class hierarchy:
- HTMLNode: Abstract base class (not used directly)
- LeafNode: Represents elements with text content but no children (e.g., <b>text</b>)
- ParentNode: Represents elements with child elements (e.g., <div><p>...</p></div>)
"""

class HTMLNode:
    """
    Abstract base class representing an HTML element in a tree structure.
    
    An HTMLNode can represent any HTML element with:
    - tag: The HTML tag name (e.g., "div", "p", "a")
    - value: Text content (used by LeafNode)
    - children: List of child HTMLNodes (used by ParentNode)
    - props: Dictionary of HTML attributes (e.g., {"href": "/link", "class": "btn"})
    
    This class is abstract and should not be instantiated directly.
    Use LeafNode or ParentNode instead.
    """
    def __init__(self, tag=None, value=None, children=None, props=None):
        self.tag = tag        # HTML tag name (e.g., "div", "p", "a")
        self.value = value    # Text content for leaf nodes
        self.children = children  # List of child HTMLNodes for parent nodes
        self.props = props    # Dictionary of HTML attributes (e.g., {"href": "/link"})

    def to_html(self):
        """
        Converts the HTMLNode tree to an HTML string.
        
        This is an abstract method that must be implemented by subclasses.
        """
        raise NotImplementedError("to_html method not implemented")

    def props_to_html(self):
        """
        Converts the props dictionary to HTML attribute string format.
        
        Returns a string like ' href="/link" class="btn"' that can be
        inserted directly into an HTML opening tag.
        
        Returns:
            str: HTML attributes string (e.g., ' href="/link" class="btn"')
                 Returns empty string if no props are defined
        """
        if self.props == None:
            return ""
        
        # Build attribute string by formatting each key-value pair
        props_html = ""
        for k, v in self.props.items():
            props_html += f' {k}="{v}"'

        return props_html
    
    def __repr__(self):
        """String representation for debugging purposes."""
        return f"HTMLNode({self.tag}, {self.value}, children: {self.children}, {self.props})"
        

class LeafNode(HTMLNode):
    """
    Represents an HTML element that contains only text content and no children.
    
    LeafNodes are used for simple elements like:
    - <b>bold text</b>
    - <i>italic text</i>
    - <a href="/link">link text</a>
    - <img src="/image.png" alt="description">
    
    A LeafNode cannot have children - it only contains text content.
    """
    def __init__(self, tag, value, props=None):
        """
        Initialize a LeafNode.
        
        Args:
            tag: HTML tag name (e.g., "b", "i", "a", "img")
            value: Text content (for images, this is the alt text)
            props: Optional dictionary of HTML attributes
        """
        super().__init__(tag, value, None, props)

    def to_html(self): #type: ignore
        """
        Converts the LeafNode to an HTML string.
        
        Returns:
            str: HTML string representation (e.g., '<b>text</b>')
        
        Raises:
            ValueError: If value is None (LeafNode must have content)
        
        Special cases:
            - If tag is None, returns just the value (plain text)
            - If props is None, omits attributes from the tag
        """
        if self.value is None:
            raise ValueError("invalid HTML: no value")
        
        # If no tag specified, return just the text content (plain text node)
        if self.tag is None:
            return self.value

        # Build HTML string with or without attributes
        if self.props == None:
            return f"<{self.tag}>{self.value}</{self.tag}>"

        # Include attributes if they exist
        return f"<{self.tag}{self.props_to_html()}>{self.value}</{self.tag}>"

    def __repr__(self):
        """String representation for debugging purposes."""
        return f"LeafNode({self.tag}, {self.value}, {self.props})"


class ParentNode(HTMLNode):
    """
    Represents an HTML element that contains child elements.
    
    ParentNodes are used for container elements like:
    - <div><p>...</p></div>
    - <ul><li>...</li><li>...</li></ul>
    - <blockquote>...</blockquote>
    
    A ParentNode cannot have a direct text value - all content comes from children.
    """
    def __init__(self, tag, children, props=None):
        """
        Initialize a ParentNode.
        
        Args:
            tag: HTML tag name (e.g., "div", "ul", "blockquote")
            children: List of HTMLNode children (can contain both LeafNodes and ParentNodes)
            props: Optional dictionary of HTML attributes
        """
        super().__init__(tag, None, children, props)

    def to_html(self): #type: ignore
        """
        Converts the ParentNode and all its children to an HTML string.
        
        This method recursively calls to_html() on all children and concatenates
        the results. The resulting HTML string represents the complete nested
        structure of the element tree.
        
        Returns:
            str: HTML string representation of the node and all its children
        
        Raises:
            ValueError: If tag is None or children is None (ParentNode must have both)
        """
        if self.tag is None:
            raise ValueError("invalid HTML: no tag")
        if self.children is None:
            raise ValueError("invalid HTML: no children")
        
        # Recursively convert all children to HTML strings
        children_html = ""
        for child in self.children:
            children_html += child.to_html()
        
        # Combine tag, attributes, and children HTML
        return f"<{self.tag}{self.props_to_html()}>{children_html}</{self.tag}>"

    def __repr__(self):
        """String representation for debugging purposes."""
        return f"ParentNode({self.tag}, children: {self.children}, {self.props})"