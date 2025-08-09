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
    public void testDirectoryRecognitionWithAsterisk() {
        // Test cases covering the new asterisk support
        List<String> testBookmarks = Arrays.asList(
            "1.1 Regular subdirectory A 10",
            "*1.1 Asterisk subdirectory B 20", 
            "* 1.1 Spaced asterisk subdirectory C 30",
            "1.2 Another regular subdirectory 40"
        );
        
        List<Bookmark> result = PDFUtil.generateBookmark(testBookmarks, 0);
        
        // Should have 4 bookmarks generated
        Assert.assertEquals("Should generate 4 bookmarks", 4, result.size());
        
        // Check that all bookmarks have proper sequences
        Assert.assertEquals("First bookmark sequence", "1.1", result.get(0).getSeq());
        Assert.assertEquals("First bookmark title", "Regular subdirectory A", result.get(0).getTitle());
        Assert.assertEquals("First bookmark page", 10, result.get(0).getPageIndex());
        
        Assert.assertEquals("Second bookmark sequence", "1.1", result.get(1).getSeq());
        Assert.assertEquals("Second bookmark title", "Asterisk subdirectory B", result.get(1).getTitle());
        Assert.assertEquals("Second bookmark page", 20, result.get(1).getPageIndex());
        
        Assert.assertEquals("Third bookmark sequence", "1.1", result.get(2).getSeq());
        Assert.assertEquals("Third bookmark title", "Spaced asterisk subdirectory C", result.get(2).getTitle());
        Assert.assertEquals("Third bookmark page", 30, result.get(2).getPageIndex());
        
        Assert.assertEquals("Fourth bookmark sequence", "1.2", result.get(3).getSeq());
        Assert.assertEquals("Fourth bookmark title", "Another regular subdirectory", result.get(3).getTitle());
        Assert.assertEquals("Fourth bookmark page", 40, result.get(3).getPageIndex());
    }
    
    @Test
    public void testAsteriskPreprocessing() {
        // Test just the asterisk removal functionality
        List<String> testBookmarks = Arrays.asList(
            "*1.1 Title 10",
            "* 1.1 Title 20", 
            "1.1 Title 30" // No asterisk
        );
        
        List<Bookmark> result = PDFUtil.generateBookmark(testBookmarks, 0);
        
        // All should be parsed as valid bookmarks with sequence "1.1"
        Assert.assertEquals("Should generate 3 bookmarks", 3, result.size());
        
        for (int i = 0; i < 3; i++) {
            Assert.assertEquals("Bookmark " + i + " should have sequence 1.1", "1.1", result.get(i).getSeq());
            Assert.assertEquals("Bookmark " + i + " should have title 'Title'", "Title", result.get(i).getTitle());
        }
    }
}