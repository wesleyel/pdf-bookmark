package test;

import com.ifnoelse.pdf.Bookmark;
import com.ifnoelse.pdf.PDFUtil;
import org.junit.Test;
import org.junit.Assert;

import java.util.Arrays;
import java.util.List;

/**
 * Test for directory recognition with asterisk patterns
 */
public class DirectoryRecognitionTest {

    @Test
    public void testAsteriskPreservationInTitle() {
        // Test cases covering the asterisk preservation requirement
        List<String> testBookmarks = Arrays.asList(
            "1.1 Regular subdirectory A 10",
            "*1.1 Asterisk subdirectory B 20", 
            "* 1.1 Spaced asterisk subdirectory C 30",
            "1.2 Another regular subdirectory 40"
        );
        
        List<Bookmark> result = PDFUtil.generateBookmark(testBookmarks, 0, Integer.MIN_VALUE, Integer.MAX_VALUE);
        
        // Should have 2 top-level bookmarks (1.1 and 1.2)
        Assert.assertEquals("Should generate 2 top-level bookmarks", 2, result.size());
        
        // Check first top-level bookmark (1.1 - should have 2 sub-bookmarks)
        Bookmark firstBookmark = result.get(0);
        Assert.assertEquals("First bookmark sequence", "1.1", firstBookmark.getSeq());
        Assert.assertEquals("First bookmark title", "Regular subdirectory A", firstBookmark.getTitle());
        Assert.assertEquals("First bookmark page", 10, firstBookmark.getPageIndex());
        Assert.assertEquals("First bookmark should have 2 sub-bookmarks", 2, firstBookmark.getSubBookMarks().size());
        
        // Check sub-bookmarks (asterisk bookmarks should be preserved)
        Bookmark subBookmark1 = firstBookmark.getSubBookMarks().get(0);
        Assert.assertEquals("Sub-bookmark 1 sequence", "1.1", subBookmark1.getSeq());
        Assert.assertEquals("Sub-bookmark 1 title", "* Asterisk subdirectory B", subBookmark1.getTitle());
        Assert.assertEquals("Sub-bookmark 1 page", 20, subBookmark1.getPageIndex());
        
        Bookmark subBookmark2 = firstBookmark.getSubBookMarks().get(1);
        Assert.assertEquals("Sub-bookmark 2 sequence", "1.1", subBookmark2.getSeq());
        Assert.assertEquals("Sub-bookmark 2 title", "* Spaced asterisk subdirectory C", subBookmark2.getTitle());
        Assert.assertEquals("Sub-bookmark 2 page", 30, subBookmark2.getPageIndex());
        
        // Check second top-level bookmark
        Bookmark secondBookmark = result.get(1);
        Assert.assertEquals("Second bookmark sequence", "1.2", secondBookmark.getSeq());
        Assert.assertEquals("Second bookmark title", "Another regular subdirectory", secondBookmark.getTitle());
        Assert.assertEquals("Second bookmark page", 40, secondBookmark.getPageIndex());
    }
    
    @Test
    public void testAsteriskRecognizedAsSubdirectories() {
        // Test that asterisk entries are recognized as subdirectories (have sequence numbers)
        // Use different sequences to avoid hierarchy conflicts
        List<String> testBookmarks = Arrays.asList(
            "*2.1 Title 10",
            "* 3.1 Title 20", 
            "4.1 Title 30" // Non-asterisk for comparison
        );
        
        List<Bookmark> result = PDFUtil.generateBookmark(testBookmarks, 0, Integer.MIN_VALUE, Integer.MAX_VALUE);
        
        // All should be parsed as valid top-level bookmarks with different sequences
        Assert.assertEquals("Should generate 3 top-level bookmarks", 3, result.size());
        
        // All should have sequence numbers (making them subdirectories when appropriate)
        Assert.assertEquals("Bookmark 0 should have sequence 2.1", "2.1", result.get(0).getSeq());
        Assert.assertEquals("Bookmark 1 should have sequence 3.1", "3.1", result.get(1).getSeq());
        Assert.assertEquals("Bookmark 2 should have sequence 4.1", "4.1", result.get(2).getSeq());
        
        // All should have non-null sequences
        for (int i = 0; i < 3; i++) {
            Assert.assertNotNull("Bookmark " + i + " should have a sequence (subdirectory capability)", result.get(i).getSeq());
        }
        
        // Check titles - first two should have asterisk preserved
        Assert.assertEquals("First asterisk bookmark title", "* Title", result.get(0).getTitle());
        Assert.assertEquals("Second asterisk bookmark title", "* Title", result.get(1).getTitle());
        Assert.assertEquals("Regular bookmark title", "Title", result.get(2).getTitle());
    }
}